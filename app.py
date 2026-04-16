import streamlit as st
import numpy as np

# -------------------------
# CORE LOGIC (คณิตศาสตร์การคำนวณ)
# -------------------------
def d2r(deg): 
    return deg * np.pi / 180.0

def wpr_to_rot(w, p, r):
    w, p, r = d2r(w), d2r(p), d2r(r)
    Rz = np.array([[np.cos(w), -np.sin(w), 0], [np.sin(w), np.cos(w), 0], [0, 0, 1]])
    Ry = np.array([[np.cos(p), 0, np.sin(p)], [0, 1, 0], [-np.sin(p), 0, np.cos(p)]])
    Rx = np.array([[1, 0, 0], [0, np.cos(r), -np.sin(r)], [0, np.sin(r), np.cos(r)]])
    return Rz @ Ry @ Rx

def rot_to_wpr_fanuc(R_mat):
    beta = np.arctan2(-R_mat[2, 0], np.sqrt(R_mat[0, 0]**2 + R_mat[1, 0]**2))
    if abs(np.cos(beta)) > 1e-10:
        alpha = np.arctan2(R_mat[1, 0], R_mat[0, 0])
        gamma = np.arctan2(R_mat[2, 1], R_mat[2, 2])
    else:
        alpha = 0.0
        gamma = np.arctan2(-R_mat[0, 1], R_mat[1, 1])
    return np.degrees(gamma), np.degrees(beta), np.degrees(alpha)

def solve_tool(vals):
    # vals: [X, Y, Z, W, P, R]
    Fx, Fz = vals[0], vals[2]
    lpos_w, lpos_p, lpos_r = vals[3], vals[4], vals[5]
    
    # FANUC Matrix order: R, P, W สำหรับการคำนวณตำแหน่ง
    A = wpr_to_rot(lpos_r, lpos_p, lpos_w)
    
    coeff = np.array([[A[0, 0], A[0, 2]], [A[2, 0], A[2, 2]]])
    rhs = np.array([-Fx, -Fz])
    sol = np.linalg.solve(coeff, rhs)
    Tx, Tz = sol
    
    # หาค่า WPR ของ Tool (Inverse Rotation)
    R_tool = A.T
    W_t, P_t, R_t = rot_to_wpr_fanuc(R_tool)
    
    return [Tx, 0.0, Tz, W_t, P_t, R_t]

# -------------------------
# STREAMLIT UI (ส่วนหน้าเว็บ)
# -------------------------
st.set_page_config(page_title="FANUC Tool Calc", page_icon="🤖", layout="centered")

st.title("🤖 FANUC Tool Frame Calculator")
st.markdown("กรอกค่า **LPOS** (UF9) เพื่อคำนวณหาค่า Tool Frame ที่ทำให้ X และ Z เป็นศูนย์")

# ส่วนรับข้อมูล Input
st.subheader("📥 Input: LPOS Data")
col1, col2 = st.columns(2)

with col1:
    x_in = st.number_input("X (mm)", value=263.655, format="%.3f")
    y_in = st.number_input("Y (mm)", value=-676.670, format="%.3f")
    z_in = st.number_input("Z (mm)", value=306.326, format="%.3f")

with col2:
    w_in = st.number_input("W (deg)", value=-176.727, format="%.3f")
    p_in = st.number_input("P (deg)", value=-3.860, format="%.3f")
    r_in = st.number_input("R (deg)", value=-43.725, format="%.3f")

if st.button("🚀 CALCULATE NEW TOOL", type="primary", use_container_width=True):
    # คำนวณผลลัพธ์
    res = solve_tool([x_in, y_in, z_in, w_in, p_in, r_in])
    
    st.divider()
    
    # ส่วนแสดงผลลัพธ์
    st.subheader("🎯 Result: New Tool Frame")
    
    # แสดงเป็นตารางเพื่อให้เห็นตัวเลขชัดเจน ไม่โดนตัด
    res_names = ["X (mm)", "Y (mm)", "Z (mm)", "W (deg)", "P (deg)", "R (deg)"]
    table_data = {
        "Axis": res_names,
        "Value": [f"{v:.3f}" for v in res]
    }
    st.table(table_data)
    
    # กล่องข้อความสำหรับก๊อปปี้ไปใช้งานง่ายๆ
    st.info("💡 Copy ค่าด้านล่างนี้ไปใส่ใน Tool Frame (X, Y, Z, W, P, R):")
    format_str = f"{res[0]:.3f}, {res[1]:.3f}, {res[2]:.3f}, {res[3]:.3f}, {res[4]:.3f