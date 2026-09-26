// Two-slit interference in a WebGL fragment shader (technique after PavelDoGreat/WebGL-Fluid-Simulation: raw WebGL,
// full-canvas shader, pointer-driven). Each pixel sums the two cylindrical waves exactly:
//   coherent:    I = |e^{ik r1}/sqrt(r1) + e^{i(k r2 + phi)}/sqrt(r2)|^2
//   which-path:  I = 1/r1 + 1/r2   (the cross term vanishes when the paths are distinguishable; P06, the quantum eraser)
// The pointer's horizontal position sets the relative phase phi, which slides the fringes. Units: 1 = one screen height.
(function () {
  const cv = document.getElementById("slit-canvas"); if (!cv) return;
  const gl = cv.getContext("webgl", { antialias: false, premultipliedAlpha: false });
  if (!gl) { cv.replaceWith(Object.assign(document.createElement("p"), { textContent: "WebGL unavailable" })); return; }
  const vs = "attribute vec2 p; varying vec2 uv; void main(){ uv = p*0.5+0.5; gl_Position = vec4(p,0.,1.); }";
  const fs = `precision highp float; varying vec2 uv;
    uniform float aspect, k, d, phi, t, which;
    void main(){
      vec2 q = vec2(uv.x*aspect, uv.y);
      vec2 s1 = vec2(0.06, 0.5 + d*0.5), s2 = vec2(0.06, 0.5 - d*0.5);
      float r1 = max(distance(q, s1), 1e-3), r2 = max(distance(q, s2), 1e-3);
      float a1 = 1.0/sqrt(r1), a2 = 1.0/sqrt(r2);
      float ph1 = k*r1 - t, ph2 = k*r2 + phi - t;
      float re = a1*cos(ph1) + a2*cos(ph2), im = a1*sin(ph1) + a2*sin(ph2);
      float Icoh = re*re + im*im, Iinc = a1*a1 + a2*a2;
      float I = mix(Icoh, Iinc, which);
      float wave = mix(re*re, a1*a1*cos(ph1)*cos(ph1) + a2*a2*cos(ph2)*cos(ph2), which);
      float screen = step(aspect - 0.06, q.x);
      float b = mix(0.18*I + 0.10*wave, 0.30*I, screen);
      b = b / (1.0 + b);
      if (q.x < 0.06) b = 0.22 * (0.5 + 0.5 * cos(k * q.x - t));   // incoming plane wave before the slits
      vec3 col = mix(vec3(0.02,0.03,0.07), mix(vec3(0.20,0.55,1.0), vec3(0.37,0.95,0.88), b), b*1.6);
      col += screen * vec3(1.0,0.55,0.30) * b * 0.6;
      if (q.x < 0.065 && q.x > 0.055 && abs(q.y - s1.y) > 0.012 && abs(q.y - s2.y) > 0.012) col = vec3(0.35,0.4,0.5);
      gl_FragColor = vec4(col, 1.0);
    }`;
  const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s; };
  const prog = gl.createProgram(); gl.attachShader(prog, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, fs)); gl.linkProgram(prog); gl.useProgram(prog);
  const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, "p"); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  const U = (n) => gl.getUniformLocation(prog, n);
  const $ = (id) => document.getElementById(id);
  let phi = 0, which = 0, whichTarget = 0, visible = false;   // starts paused; the observer turns it on when on screen
  cv.addEventListener("pointermove", (e) => { const r = cv.getBoundingClientRect(); phi = ((e.clientX - r.left) / r.width) * 2 * Math.PI; });
  $("slit-which").addEventListener("change", (e) => (whichTarget = e.target.checked ? 1 : 0));
  new IntersectionObserver((es) => (visible = es[0].isIntersecting)).observe(cv);
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  function readout() {
    const lam = +$("slit-lambda").value, d = +$("slit-d").value, L = cv.width / cv.height - 0.06 - 0.06;
    $("slit-info").innerHTML = `λ = <b>${lam.toFixed(3)}</b> · d = <b>${d.toFixed(2)}</b> · screen at L = <b>${L.toFixed(2)}</b> (screen heights)<br>` +
      `fringe spacing λL/d = <b>${(lam * L / d).toFixed(3)}</b> · relative phase φ = <b>${(phi / Math.PI).toFixed(2)}π</b> (move the pointer)<br>` +
      (whichTarget ? `which-path information present: <b class="bad">no fringes</b>` : `paths indistinguishable: <b class="ok">fringes</b>`);
  }
  ["slit-lambda", "slit-d", "slit-which"].forEach((id) => $(id).addEventListener("input", readout));
  function frame(now) {
    if (visible) {
      const w = Math.min(cv.clientWidth, 1400), h = w * cv.clientHeight / Math.max(1, cv.clientWidth), dpr = Math.min(devicePixelRatio, 1);
      if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
      gl.viewport(0, 0, cv.width, cv.height);
      which += (whichTarget - which) * 0.08;
      gl.uniform1f(U("aspect"), cv.width / cv.height); gl.uniform1f(U("k"), 2 * Math.PI / +$("slit-lambda").value);
      gl.uniform1f(U("d"), +$("slit-d").value); gl.uniform1f(U("phi"), phi); gl.uniform1f(U("t"), reduce ? 0 : now * 0.004); gl.uniform1f(U("which"), which);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      if (Math.floor(now / 200) % 2 === 0) readout();
    }
    requestAnimationFrame(frame);
  }
  readout(); requestAnimationFrame(frame);
})();
