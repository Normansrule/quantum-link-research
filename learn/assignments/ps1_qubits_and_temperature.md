# Problem Set 1 — Qubits, Noise, Temperature

Read `learn/00_foundations/03`, `06` and `learn/02_qubit_modalities/10` first. Numerical answers go in `learn/assignments/answers.py` as the named variables; check with `python -m pytest tests/test_assignments.py -k ps1`.

1. **Bloch vector.** A qubit is in the state $\cos(\theta/2)|0\rangle+e^{i\varphi}\sin(\theta/2)|1\rangle$ with $\theta=\pi/3$, $\varphi=\pi/4$. Give the Bloch vector $(r_x,r_y,r_z)$ to three decimals. *(`ps1_bloch`)*
2. **Thermal occupation.** How many thermal photons per mode does a 6 GHz transmon see at 20 mK? At 300 K? Give both to two significant figures. *(`ps1_nbar_cold`, `ps1_nbar_hot`)*
3. **T₁ shortening.** A qubit has $T_1=100\,\mu$s at zero temperature. Using $T_1(T)=T_1(0)/(2\bar n+1)$, what is $T_1$ at 100 mK for a 6 GHz qubit? *(`ps1_t1_100mK`, in seconds)*
4. **A channel is a map.** Write the two Kraus operators of amplitude damping with $\gamma=0.3$ and verify $\sum E_k^\dagger E_k=I$. Give the average gate fidelity of the depolarizing channel with $p=0.1$. *(`ps1_avg_fid_depol`)*
5. *(written)* Why can an optical photon cross a room-temperature channel while a microwave photon cannot? Use the number from question 2.
6. *(written)* In one paragraph, explain what "temperature is mandatory" (INV-6) prevents a careless simulation from doing.
