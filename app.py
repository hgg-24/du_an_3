import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sympy as sp

# ==========================================
# 1. PAGE CONFIG & CUSTOM CSS (UI/UX)
# ==========================================
st.set_page_config(page_title="ED-ODYSSEY: 3D Vector Lab", layout="wide", page_icon="🧊")

st.markdown("""
<style>
/* Bo góc 20px, Neumorphism shadow, viền mảnh cho các block nội dung */
div[data-testid="stVerticalBlock"] > div {
    background-color: #ffffff;
    border-radius: 20px;
    padding: 1.2rem;
    box-shadow: 6px 6px 12px #e0e5ec, -6px -6px 12px #ffffff;
    border: 1px solid #eef2f5;
    margin-bottom: 1rem;
}
/* Ẩn header của Data Editor để UI clean hơn */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MAIN APPLICATION LOGIC
# ==========================================
def main():
    st.title("🧊 ED-ODYSSEY: 3D Vector & Oxyz Lab")
    
    try:
        # --- KHÔNG GIAN NHẬP LIỆU 3D (DYNAMIC DATAFRAME) ---
        st.subheader("1. Không Gian Khởi Tạo Vector")
        
        # Dữ liệu mặc định: 3 vector không đồng phẳng
        default_data = {
            "Tên Vector": ["a", "b", "c"],
            "x_Đầu": [0.0, 0.0, 0.0],
            "y_Đầu": [0.0, 0.0, 0.0],
            "z_Đầu": [0.0, 0.0, 0.0],
            "x_Cuối": [2.0, 1.0, 0.0],
            "y_Cuối": [0.0, 3.0, 1.0],
            "z_Cuối": [1.0, -1.0, 3.0]
        }
        df = pd.DataFrame(default_data)
        
        edited_df = st.data_editor(
            df, 
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True
        )

        # Xử lý dữ liệu DataFrame thành Dictionary chứa Numpy Arrays
        vectors = {}
        for index, row in edited_df.iterrows():
            name = str(row["Tên Vector"]).strip()
            if name:
                start_pt = np.array([float(row["x_Đầu"]), float(row["y_Đầu"]), float(row["z_Đầu"])])
                end_pt = np.array([float(row["x_Cuối"]), float(row["y_Cuối"]), float(row["z_Cuối"])])
                vec_val = end_pt - start_pt
                vectors[name] = {
                    'start': start_pt,
                    'end': end_pt,
                    'vec': vec_val
                }

        # --- BỐ CỤC CHÍNH: CỘT TRÁI (TÍNH TOÁN) - CỘT PHẢI (ĐỒ THỊ 3D) ---
        col_math, col_plot = st.columns([1, 1.2])
        
        additional_plot_traces = [] # Lưu trữ các vector sinh ra từ phép toán để vẽ thêm

        with col_math:
            st.subheader("2. Lab Toán Học Oxyz")
            tab1, tab2, tab3 = st.tabs(["Tích Vô/Có Hướng", "Tích Hỗn Tạp", "Đại Số Vector"])
            
            vec_names = list(vectors.keys())
            
            # ----------------------------------------
            # TAB 1: TÍCH VÔ HƯỚNG & CÓ HƯỚNG
            # ----------------------------------------
            with tab1:
                if len(vec_names) >= 2:
                    c1, c2 = st.columns(2)
                    v1_name = c1.selectbox("Chọn vector thứ nhất", vec_names, key="t1_v1")
                    v2_name = c2.selectbox("Chọn vector thứ hai", vec_names, index=1, key="t1_v2")
                    
                    v1 = vectors[v1_name]['vec']
                    v2 = vectors[v2_name]['vec']
                    
                    # Tính toán Tích vô hướng & Góc
                    dot_product = np.dot(v1, v2)
                    norm_v1 = np.linalg.norm(v1)
                    norm_v2 = np.linalg.norm(v2)
                    
                    st.markdown("**Tích vô hướng & Thông số:**")
                    st.latex(rf"\vec{{{v1_name}}} \cdot \vec{{{v2_name}}} = {dot_product:.2f}")
                    st.latex(rf"|\vec{{{v1_name}}}| = {norm_v1:.2f} \quad ; \quad |\vec{{{v2_name}}}| = {norm_v2:.2f}")
                    
                    if norm_v1 * norm_v2 != 0:
                        cos_theta = dot_product / (norm_v1 * norm_v2)
                        # Xử lý sai số dấu phẩy động
                        cos_theta = np.clip(cos_theta, -1.0, 1.0)
                        theta_rad = np.arccos(cos_theta)
                        theta_deg = np.degrees(theta_rad)
                        st.latex(rf"\cos(\vec{{{v1_name}}}, \vec{{{v2_name}}}) = {cos_theta:.4f} \implies \theta \approx {theta_deg:.2f}^\circ")
                    
                    # Tính Tích có hướng
                    cross_product = np.cross(v1, v2)
                    st.markdown("**Tích có hướng (Cross Product):**")
                    st.latex(rf"[\vec{{{v1_name}}}, \vec{{{v2_name}}}] = ({cross_product[0]:.2f}; {cross_product[1]:.2f}; {cross_product[2]:.2f})")
                    
                    if st.checkbox(f"Trực quan hóa vector [\vec{{{v1_name}}}, \vec{{{v2_name}}}]", key="chk_cross"):
                        additional_plot_traces.append({
                            'start': np.array([0,0,0]), # Vector tự do vẽ từ gốc
                            'end': cross_product,
                            'name': f"[{v1_name},{v2_name}]",
                            'color': '#FF9F1C' # Màu cam nổi bật
                        })
                else:
                    st.info("Vui lòng tạo ít nhất 2 vector trong bảng dữ liệu.")

            # ----------------------------------------
            # TAB 2: TÍCH HỖN TẠP & THỂ TÍCH
            # ----------------------------------------
            with tab2:
                if len(vec_names) >= 3:
                    c1, c2, c3 = st.columns(3)
                    v1_name = c1.selectbox("Vector 1", vec_names, key="t2_v1")
                    v2_name = c2.selectbox("Vector 2", vec_names, index=1, key="t2_v2")
                    v3_name = c3.selectbox("Vector 3", vec_names, index=2, key="t2_v3")
                    
                    v1 = vectors[v1_name]['vec']
                    v2 = vectors[v2_name]['vec']
                    v3 = vectors[v3_name]['vec']
                    
                    # Tính toán Tích hỗn tạp
                    cross_v1_v2 = np.cross(v1, v2)
                    triple_product = np.dot(cross_v1_v2, v3)
                    vol = abs(triple_product)
                    
                    st.markdown("**Tích hỗn tạp:**")
                    st.latex(rf"[\vec{{{v1_name}}}, \vec{{{v2_name}}}] \cdot \vec{{{v3_name}}} = {triple_product:.2f}")
                    
                    if np.isclose(vol, 0, atol=1e-5):
                        st.warning("3 vector này ĐỒNG PHẲNG.")
                        st.latex(rf"V = 0 \implies \text{{Đồng phẳng}}")
                    else:
                        st.success("3 vector KHÔNG đồng phẳng. Khởi tạo khối hình học:")
                        st.latex(rf"V_{{Hộp}} = \big|[\vec{{{v1_name}}}, \vec{{{v2_name}}}] \cdot \vec{{{v3_name}}}\big| = {vol:.2f}")
                        st.latex(rf"V_{{Tứ \, diện}} = \frac{{1}}{{6}} V_{{Hộp}} \approx {vol/6:.2f}")
                else:
                    st.info("Vui lòng tạo ít nhất 3 vector trong bảng dữ liệu.")

            # ----------------------------------------
            # TAB 3: PHÉP CỘNG ĐẠI SỐ
            # ----------------------------------------
            with tab3:
                st.markdown("**Nhập biểu thức (vd: `2*a - b + 3*c`):**")
                formula = st.text_input("Biểu thức:", value="a + b" if len(vec_names)>=2 else "")
                
                if formula:
                    try:
                        # Parsing bằng sympy
                        expr = sp.sympify(formula)
                        free_vars = list(expr.free_symbols)
                        var_names_in_expr = [str(v) for v in free_vars]
                        
                        missing_vars = [v for v in var_names_in_expr if v not in vectors]
                        
                        if missing_vars:
                            st.error(f"Biến không tồn tại trong bảng: {', '.join(missing_vars)}")
                        else:
                            # Chuyển đổi biểu thức sympy thành hàm python có thể xử lý numpy arrays
                            lambdified_func = sp.lambdify(free_vars, expr, modules='numpy')
                            args = [vectors[v]['vec'] for v in var_names_in_expr]
                            result_vec = lambdified_func(*args)
                            
                            st.latex(rf"\vec{{R}} = {sp.latex(expr)} = ({result_vec[0]:.2f}; {result_vec[1]:.2f}; {result_vec[2]:.2f})")
                            
                            additional_plot_traces.append({
                                'start': np.array([0,0,0]),
                                'end': result_vec,
                                'name': f"R = {formula}",
                                'color': '#E71D36' # Đỏ rực
                            })
                    except Exception as e:
                        st.error(f"Lỗi cú pháp toán học. Chi tiết: {e}")

        # --- CỘT PHẢI: TRỰC QUAN HÓA 3D BẰNG PLOTLY ---
        with col_plot:
            fig = go.Figure()
            
            # Vẽ các vector gốc
            colors = ['#007AFF', '#34C759', '#5856D6', '#FF2D55', '#AF52DE']
            for i, (name, data) in enumerate(vectors.items()):
                c_color = colors[i % len(colors)]
                p_start = data['start']
                p_end = data['end']
                
                # Vẽ thân vector (Đường thẳng)
                fig.add_trace(go.Scatter3d(
                    x=[p_start[0], p_end[0]], 
                    y=[p_start[1], p_end[1]], 
                    z=[p_start[2], p_end[2]],
                    mode='lines',
                    line=dict(width=6, color=c_color),
                    name=f'Thân {name}',
                    showlegend=False
                ))
                
                # Vẽ ngọn vector (Diamond marker + Text)
                fig.add_trace(go.Scatter3d(
                    x=[p_end[0]], y=[p_end[1]], z=[p_end[2]],
                    mode='markers+text',
                    marker=dict(size=6, symbol='diamond', color=c_color),
                    text=[rf"<b>{name}</b>"], textposition="top center",
                    name=f'Vector {name}',
                    textfont=dict(size=14, color=c_color)
                ))

            # Vẽ các vector bổ sung (Từ Tab 1 và Tab 3)
            for trace in additional_plot_traces:
                p_start = trace['start']
                p_end = trace['end']
                t_color = trace['color']
                t_name = trace['name']
                
                fig.add_trace(go.Scatter3d(
                    x=[p_start[0], p_end[0]], y=[p_start[1], p_end[1]], z=[p_start[2], p_end[2]],
                    mode='lines', line=dict(width=8, color=t_color, dash='dash'),
                    showlegend=False
                ))
                fig.add_trace(go.Scatter3d(
                    x=[p_end[0]], y=[p_end[1]], z=[p_end[2]],
                    mode='markers+text', marker=dict(size=8, symbol='diamond', color=t_color),
                    text=[rf"<b>{t_name}</b>"], textposition="top center",
                    textfont=dict(size=14, color=t_color),
                    name=t_name
                ))

            # Thiết lập hiển thị trục Oxyz (Lưới chuẩn & aspectmode='cube')
            max_range = np.max(np.abs(edited_df.iloc[:, 1:].values)) if not edited_df.empty else 5.0
            max_range = max(max_range, 5.0) + 1.0 # Buffer

            fig.update_layout(
                margin=dict(l=0, r=0, b=0, t=0),
                paper_bgcolor='rgba(0,0,0,0)',
                scene=dict(
                    aspectmode='cube', # Tỉ lệ 1:1:1 tuyệt đối
                    xaxis=dict(range=[-max_range, max_range], showgrid=True, gridcolor='lightgray', zeroline=True, zerolinewidth=2, zerolinecolor='black', title="Trục X"),
                    yaxis=dict(range=[-max_range, max_range], showgrid=True, gridcolor='lightgray', zeroline=True, zerolinewidth=2, zerolinecolor='black', title="Trục Y"),
                    zaxis=dict(range=[-max_range, max_range], showgrid=True, gridcolor='lightgray', zeroline=True, zerolinewidth=2, zerolinecolor='black', title="Trục Z"),
                    camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)) # Góc nhìn Default chuẩn
                ),
                showlegend=False,
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Cảnh báo hệ thống (Exception): Có lỗi xảy ra trong quá trình tính toán hoặc render dữ liệu. Chi tiết lỗi: {e}")

if __name__ == "__main__":
    main()
