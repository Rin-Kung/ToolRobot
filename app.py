import streamlit as st
import numpy as np

# --- Logic คำนวณเดิม (คงไว้) ---
def d2r(deg): return deg * np.pi / 180.0

def wpr_to_rot(w, p, r):
    w, p, r = d2r(w), d2r(p), d2r(r)
    Rz = np.array([[np.cos(w), -np.sin(w), 0], [np.sin(w), np.cos(w), 0], [0, 0, 1]])
    Ry = np.array([[np.cos(p), 0, np.sin(p)], [0, 1, 0], [-np.sin(p), 0, np.cos(p)]])
    Rx = np.array([[1, 0, 0], [0, np.cos(r), -np.sin(r)], [0, np.sin(r), np.cos(r)]])
    return Rz @ Ry @ Rx

def rot_to_wpr_fanuc(R_mat):
    beta = np.arctan2(-R_mat[2, 0], np.sqrt(R_mat[0, 0]**2 + R_mat[1, 0]**2))
    if abs(np.cos(beta)) > 1e-10:
        alpha = np.arctan2(R_mat[1, 0], R_mat[0, 0]); gamma = np.arctan2(R_mat[2, 1], R_mat[2, 2])
    else:
        alpha = 0.0; gamma = np.arctan2(-R_mat[0, 1], R_mat[1, 1])
    return np.degrees(gamma), np.degrees(beta), np.degrees(alpha)

def solve_tool(vals):
    Fx, Fz = vals[0], vals[2]
    A = wpr_to_rot(vals[5], vals[4], vals[3]) # R, P, W order
    coeff = np.array([[A[0, 0], A[0, 2]], [A[2, 0], A[2, 2]]])
    rhs = np.array([-Fx, -Fz])
    sol = np.linalg.solve(coeff, rhs)
    R_tool = A.T
    W_t, P_t, R_t = rot_to_wpr_fanuc(R_tool)
    return [sol[0], 0.0, sol[1], W_t, P_t, R_t]

# --- ส่วนของการสร้างหน้าเว็บ ---
st.set_page_config(page_title="FANUC Tool Calc", page_icon="🤖")
st.title("🤖 FANUC Tool Frame Calculator")
st.markdown("กรอกค่า **LPOS** จากหน้าจอ Robot (UF9)")

# สร้าง 2 คอลัมน์สำหรับ Input
col1, col2 = st.columns(2)
with col1:
    x = st.number_input("X (mm)", value=263.655, format="%.3f")
    y = st.number_input("Y (mm)", value=-676.670, format="%.3f")
    z = st.number_input("Z (mm)", value=306.326, format="%.3f")
with col2:
    w = st.number_input("W (deg)", value=-176.727, format="%.3f")
    p = st.number_input("P (deg)", value=-3.860, format="%.3f")
    r = st.number_input("R (deg)", value=-43.725, format="%.3f")

if st.button("CALCULATE NEW TOOL", type="primary", use_container_width=True):
    result = solve_tool([x, y, z, w, p, r])
    
    st.divider()
    st.subheader("🎯 Result: New Tool Frame")
    
    # แสดงผลเป็นตารางหรือการ์ด
    res_names = ["X", "Y", "Z", "W", "P", "R"]
    cols = st.columns(6)
    for i, name in enumerate(res_names):
        cols[i].metric(label=name, value=f"{result[i]:.2f}" if i < 3 else f"{result[i]:.3f}")
    
    st.success(f"Copy values to Tool Frame: `[{result[0]:.2f}, {result[1]:.2f}, {result[2]:.2f}, {result[3]:.3f}, {result[4]:.3f}, {result[5]:.3f}]`")