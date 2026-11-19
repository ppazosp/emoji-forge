({ vertex, fragments, size }) => {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = size;
  const gl = canvas.getContext("webgl2", { alpha: true, premultipliedAlpha: false, antialias: false });
  if (!gl || !gl.getExtension("EXT_color_buffer_float")) {
    throw new Error("WebGL 2 with floating-point color buffers is required");
  }

  function compile(type, code) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, code);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      throw new Error(gl.getShaderInfoLog(shader));
    }
    return shader;
  }

  const vertexShader = compile(gl.VERTEX_SHADER, vertex);
  const programs = fragments.map((code) => {
    const program = gl.createProgram();
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, compile(gl.FRAGMENT_SHADER, code));
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      throw new Error(gl.getProgramInfoLog(program));
    }
    return program;
  });

  function texture(floatingPoint) {
    const tex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texStorage2D(gl.TEXTURE_2D, 1, floatingPoint ? gl.RGBA16F : gl.RGBA8, size, size);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    return tex;
  }

  function framebuffer(tex) {
    const buffer = gl.createFramebuffer();
    gl.bindFramebuffer(gl.FRAMEBUFFER, buffer);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
    if (gl.checkFramebufferStatus(gl.FRAMEBUFFER) !== gl.FRAMEBUFFER_COMPLETE) {
      throw new Error("Could not attach float render target");
    }
    return buffer;
  }

  const art = texture(false);
  const [base, ping, pong] = [texture(true), texture(true), texture(true)];
  const targets = [base, ping, pong].map(framebuffer);
  const sources = [art, base, ping, pong, base];
  const destinations = [...targets, targets[1], null];
  gl.viewport(0, 0, size, size);

  window.renderCel = ([encodedPixels, uniforms]) => {
    const pixels = Uint8Array.from(atob(encodedPixels), (char) => char.charCodeAt(0));
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, art);
    gl.texSubImage2D(gl.TEXTURE_2D, 0, 0, 0, size, size, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
    for (const [index, program] of programs.entries()) {
      gl.useProgram(program);
      gl.bindFramebuffer(gl.FRAMEBUFFER, destinations[index]);
      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, sources[index]);
      gl.activeTexture(gl.TEXTURE1);
      gl.bindTexture(gl.TEXTURE_2D, index === 4 ? ping : null);
      gl.uniform1i(gl.getUniformLocation(program, "source"), 0);
      gl.uniform1i(gl.getUniformLocation(program, "glow"), 1);
      for (const [key, value] of Object.entries(uniforms)) {
        const location = gl.getUniformLocation(program, key);
        if (Array.isArray(value)) gl.uniform2fv(location, value);
        else gl.uniform1f(location, value);
      }
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      const error = gl.getError();
      if (error !== gl.NO_ERROR) throw new Error(`WebGL pass ${index + 1} failed: ${error}`);
    }
    return canvas.toDataURL("image/png").split(",")[1];
  };
}
