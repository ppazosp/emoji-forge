"""Render fragment effects over timed RGBA cels with ModernGL or headless WebGL 2."""

import base64
import json
from io import BytesIO
from pathlib import Path

from PIL import Image

if __package__:
    from .common import cli, image, read_timing
else:
    from common import cli, image, read_timing

SCRIPT_DIR = Path(__file__).resolve().parent
SHADERS = SCRIPT_DIR / "shaders"
if not SHADERS.is_dir():
    SHADERS = SCRIPT_DIR.parent / "shaders"
VERTEX = """
out vec2 uv;
void main() {
    uv = vec2((gl_VertexID << 1) & 2, gl_VertexID & 2);
    gl_Position = vec4(uv * 2.0 - 1.0, 0.0, 1.0);
}
"""
HEADER = """
in vec2 uv;
out vec4 result;
uniform sampler2D source;
uniform sampler2D glow;
uniform vec2 resolution;
uniform vec2 anchor;
uniform float phase;
uniform float seconds;
uniform float intensity;
"""
PASSES = [
    "result = effect(uv, cel(uv));",
    "vec4 c = texture(source, uv); result = vec4(brightPass(c), 1.0);",
    "result = blurPass(source, uv, vec2(1.0, 0.0) / resolution);",
    "result = blurPass(source, uv, vec2(0.0, 1.0) / resolution);",
    """vec4 c = texture(source, uv);
       vec3 light = texture(glow, uv).rgb * 0.40;
       vec4 base = over(c, vec4(0.68, 0.83, 1.0, clamp(length(light), 0.0, 0.45)));
       result = vec4(clamp(base.rgb + light, 0.0, 1.0), base.a * edgeFade(uv));""",
]


class ContextUnavailable(RuntimeError):
    pass


def program_sources(effect, version):
    library = (SHADERS / "library.glsl").read_text(encoding="utf-8")
    fragments = []
    for index, body in enumerate(PASSES):
        custom = effect if index == 0 else ""
        fragments.append(f"{version}{HEADER}{library}\n{custom}\nvoid main() {{ {body} }}")
    return version + VERTEX, fragments


def modern_context():
    try:
        import moderngl
    except ImportError as error:
        raise ContextUnavailable("install moderngl and glcontext") from error
    for options in ({}, {"backend": "egl"}):
        try:
            return moderngl.create_standalone_context(require=330, **options)
        except Exception as error:  # noqa: BLE001 - glcontext raises plain Exception on backend failure.
            last_error = error
    raise ContextUnavailable(str(last_error))


def render_modern(context, effect, frames, size):
    vertex, fragments = program_sources(effect, "#version 330\n")
    programs = [context.program(vertex_shader=vertex, fragment_shader=fragment) for fragment in fragments]
    arrays = [context.vertex_array(program, []) for program in programs]
    textures = [context.texture((size, size), 4, dtype="f2") for _ in range(3)]
    art = context.texture((size, size), 4)
    output = context.texture((size, size), 4)
    for texture in [art, output, *textures]:
        texture.repeat_x = texture.repeat_y = False
        texture.filter = (9728, 9728)  # GL_NEAREST
    base, ping, pong = textures
    destinations = [context.framebuffer([texture]) for texture in (base, ping, pong, ping, output)]
    for pixels, uniforms in frames:
        art.write(pixels)
        for program, array, target, source in zip(
            programs, arrays, destinations, (art, base, ping, pong, base), strict=True
        ):
            source.use(0)
            ping.use(1)
            for name, value in {"source": 0, "glow": 1, **uniforms}.items():
                if name in program:
                    program[name].value = value
            target.use()
            array.render(mode=4, vertices=3)  # GL_TRIANGLES
        raw = destinations[-1].read(components=4, alignment=1)
        yield Image.frombytes("RGBA", (size, size), raw).transpose(Image.Transpose.FLIP_TOP_BOTTOM)


def render_webgl(effect, frames, size, channel):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise ValueError("WebGL fallback needs playwright; see references/shaders.md") from error
    vertex, fragments = program_sources(effect, "#version 300 es\nprecision highp float;\n")
    js = (Path(__file__).with_name("webgl.js")).read_text(encoding="utf-8")
    with sync_playwright() as playwright:
        options = {"channel": channel} if channel else {}
        with playwright.chromium.launch(
            args=["--enable-unsafe-swiftshader"], **options
        ) as browser:
            page = browser.new_page()
            page.evaluate(js, {"vertex": vertex, "fragments": fragments, "size": size})
            for pixels, uniforms in frames:
                result = page.evaluate(
                    "args => window.renderCel(args)",
                    [base64.b64encode(pixels).decode("ascii"), uniforms],
                )
                with Image.open(BytesIO(base64.b64decode(result))) as rendered:
                    yield rendered.convert("RGBA")


def configure(parser):
    parser.add_argument("timing", type=Path)
    parser.add_argument("effect", type=Path)
    parser.add_argument("output", type=Path, help="new directory")
    parser.add_argument("--size", type=int)
    parser.add_argument("--draft", action="store_true", help="render at 128px unless --size is set")
    parser.add_argument("--backend", choices=["auto", "moderngl", "webgl"], default="auto")
    parser.add_argument("--channel", help="browser channel for WebGL, e.g. chrome")


def render(args):
    if args.size is None:
        args.size = 128 if args.draft else 512
    if args.size < 1:
        raise ValueError("size must be positive")
    rows, delays = read_timing(args.timing)
    effect = args.effect.read_text(encoding="utf-8")
    context = None
    if args.backend != "webgl":
        try:
            context = modern_context()
        except ContextUnavailable as error:
            if args.backend == "moderngl":
                raise
            print(f"ModernGL context unavailable ({error}); trying headless WebGL")

    def inputs():
        start = 0
        duration = sum(delays)
        for row, ms in zip(rows, delays, strict=True):
            cel = image(args.timing.parent / row["file"])
            if cel.width != cel.height:
                raise ValueError("shader renderer expects square source cels")
            cel = cel.resize((args.size, args.size), Image.Resampling.LANCZOS)
            pixels = cel.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes()
            uniforms = {
                "anchor": row.get("anchor", [0.5, 0.5]),
                "resolution": [args.size, args.size],
                "seconds": start * row.get("speed", 1) / 1000,
                "intensity": row.get("intensity", 1), "phase": start / duration,
            }
            yield pixels, uniforms
            start += ms

    output = (
        render_modern(context, effect, inputs(), args.size) if context else
        render_webgl(effect, inputs(), args.size, args.channel)
    )
    args.output.mkdir(parents=True, exist_ok=False)
    results = []
    try:
        for index, (frame, row) in enumerate(zip(output, rows, strict=True), 1):
            name = f"{index:03d}.png"
            frame.save(args.output / name)
            results.append({"file": name, "ms": row["ms"]})
        (args.output / "timing.json").write_text(json.dumps({"frames": results}, indent=2) + "\n")
        print(f"{len(results)} frames rendered with {'ModernGL' if context else 'WebGL 2'}")
    finally:
        output.close()
        if context:
            context.release()


if __name__ == "__main__":
    cli(__doc__, configure, render)
