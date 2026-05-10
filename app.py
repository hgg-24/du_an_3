import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sympy as sp

# ==========================================
# 1. PAGE CONFIG & CUSTOM CSS (APPLE STYLE)
# ==========================================
st.set_page_config(page_title="ED-ODYSSEY: 3D Vector Lab", layout="wide", page_icon="🧊")

st.markdown("""
<style>
/* Bo góc 20px, Neumorphism shadow cho các khối nội dung container */
div[data-testid="stVerticalBlock"] > div {
    background-color: #ffffff;
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    border: 1px solid #f0f0f5;
    margin-bottom: 1rem;
}

/* Sửa lỗi nút bấm: Nút bấm vuông vắn, font chữ gọn gàng */
div[data-testid="stButton"] > button {
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.2s ease;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0, 122, 255, 0.2);
}

/* Ẩn header của Data Editor để UI clean hơn */
[data-testid="stDataFrame"] {
    border-radius: 12px;
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
        # --- KHÔNG GIAN NHẬP LIỆU 3D ---
        st.subheader("1. Không Gian Khởi Tạo Vector")
        
        default_data = {
            "Tên Vector": ["a", "b", "c"],
            "x_Đầu": [0.0, 0.0, 0.0],
            "y_Đầu": [0.0, 0.0, 0.0],
            "z_Đầu": [0.0, 0.0, 0.0],
            "x_Cuối": [3.0, 1.0, 0.0],
            "y_Cuối": [0.0, 4.0, 2.0],
            "z_Cuối": [2.0, -1.0, 4.0]
        }
        df = pd.DataFrame(default_data)
        
        edited_df = st.data_editor(
            df, 
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True
        )

        vectors = {}
        for index, row in edited_df.iterrows():
            name = str(row["Tên Vector"]).strip()
            if name:
                start_pt = np.array([float(row["x_Đầu"]), float(row["y_Đầu"]), float(row["z_Đầu"])])
                end_pt = np.array([float(row["x_Cuối"]), float(row["y_Cuối"]), float(row["z_Cuối"])])
                vectors[name] = {
                    'start': start_pt,
                    'end': end_pt,
                    'vec': end_pt - start_pt
                }

        col_math, col_plot = st.columns([1, 1.3])
        additional_plot_traces = [] 

        with col_math:
            st.subheader("2. Lab Toán Học Oxyz")
            tab1, tab2, tab3 = st.tabs(["Tích Vô/Có Hướng", "Tích Hỗn Tạp", "Đại Số Vector"])
            vec_names = list(vectors.keys())
            
            # ----------------------------------------
            # TAB 1: TÍCH VÔ HƯỚNG & CÓ HƯỚNG
            # LƯU Ý: SỬ DỤNG RAW STRING rf"..." ĐỂ FIX LỖI LATEX
            # ----------------------------------------
            with tab1:
                if len(vec_names) >= 2:
                    c1, c2 = st.columns(2)
                    v1_n = c1.selectbox("Vector thứ nhất", vec_names, key="t1_v1")
                    v2_n = c2.selectbox("Vector thứ hai", vec_names, index=1, key="t1_v2")
                    
                    v1 = vectors[v1_n]['vec']
                    v2 = vectors[v2_n]['vec']
                    
                    dot_product = np.dot(v1, v2)
                    norm_v1 = np.linalg.norm(v1)
                    norm_v2 = np.linalg.norm(v2)
                    
                    st.markdown("**Tích vô hướng & Thông số:**")
                    st.latex(rf"\vec{{{v1_n}}} \cdot \vec{{{v2_n}}} = {dot_product:.2f}")
                    st.latex(rf"|\vec{{{v1_n}}}| = {norm_v1:.2f} \quad ; \quad |\vec{{{v2_n}}}| = {norm_v2:.2f}")
                    
                    if norm_v1 * norm_v2 != 0:
                        cos_theta = np.clip(dot_product / (norm_v1 * norm_v2), -1.0, 1.0)
                        theta_deg = np.degrees(np.arccos(cos_theta))
                        st.latex(rf"\cos(\vec{{{v1_n}}}, \vec{{{v2_n}}}) = {cos_theta:.4f} \implies \approx {theta_deg:.2f}^\circ")
                    
                    cross_product = np.cross(v1, v2)
                    st.markdown("**Tích có hướng (Cross Product):**")
                    st.latex(rf"[\vec{{{v1_n}}}, \vec{{{v2_n}}}] = ({cross_product[0]:.2f}; {cross_product[1]:.2f}; {cross_product[2]:.2f})")
                    
                    if st.checkbox(f"Trực quan hóa vector vuông góc", key="chk_cross"):
                        additional_plot_traces.append({
                            'start': np.array([0,0,0]),
                            'end': cross_product,
                            'name': f"[{v1_n},{v2_n}]",
                            'color': '#FF9F1C' # Orange
                        })
                else:
                    st.info("Cần ít nhất 2 vector.")

            # ----------------------------------------
            # TAB 2: TÍCH HỖN TẠP & THỂ TÍCH
            # ----------------------------------------
            with tab2:
                if len(vec_names) >= 3:
                    c1, c2, c3 = st.columns(3)
                    v1_n = c1.selectbox("Vector 1", vec_names, key="t2_v1")
                    v2_n = c2.selectbox("Vector 2", vec_names, index=1, key="t2_v2")
                    v3_n = c3.selectbox("Vector 3", vec_names, index=2, key="t2_v3")
                    
                    v1 = vectors[v1_n]['vec']
                    v2 = vectors[v2_n]['vec']
                    v3 = vectors[v3_n]['vec']
                    
                    triple_product = np.dot(np.cross(v1, v2), v3)
                    vol = abs(triple_product)
                    
                    st.markdown("**Tích hỗn tạp:**")
                    st.latex(rf"[\vec{{{v1_n}}}, \vec{{{v2_n}}}] \cdot \vec{{{v3_n}}} = {triple_product:.2f}")
                    
                    if np.isclose(vol, 0, atol=1e-5):
                        st.warning("3 vector này ĐỒNG PHẲNG.")
                        st.latex(rf"V = 0 \implies \text{{Đồng phẳng}}")
                    else:
                        st.success("Tạo thành khối hình học không gian:")
                        st.latex(rf"V_{{Hộp}} = \big|[\vec{{{v1_n}}}, \vec{{{v2_n}}}] \cdot \vec{{{v3_n}}}\big| = {vol:.2f}")
                        st.latex(rf"V_{{Tứ\,diện}} = \frac{{1}}{{6}} V_{{Hộp}} \approx {vol/6:.2f}")
                else:
                    st.info("Cần ít nhất 3 vector.")

            # ----------------------------------------
            # TAB 3: PHÉP CỘNG ĐẠI SỐ (n-Vector Sum)
            # ----------------------------------------
            with tab3:
                st.markdown("**Nhập biểu thức (vd: `a + 2*b - c`):**")
                formula = st.text_input("Biểu thức:", value="a + b" if len(vec_names)>=2 else "")
                
                if formula:
                    try:
                        expr = sp.sympify(formula)
                        free_vars = [str(v) for v in expr.free_symbols]
                        missing = [v for v in free_vars if v not in vectors]
                        
                        if missing:
                            st.error(f"Biến không tồn tại: {', '.join(missing)}")
                        else:
                            lambdified_func = sp.lambdify(list(expr.free_symbols), expr, modules='numpy')
                            args = [vectors[v]['vec'] for v in free_vars]
                            result_vec = lambdified_func(*args)
                            
                            st.latex(rf"\vec{{R}} = {sp.latex(expr)} = ({result_vec[0]:.2f}; {result_vec[1]:.2f}; {result_vec[2]:.2f})")
                            
                            additional_plot_traces.append({
                                'start': np.array([0,0,0]),
                                'end': result_vec,
                                'name': f"R = {formula}",
                                'color': '#FF2D55' # Apple Red
                            })
                    except Exception:
                        st.warning("Đang chờ bạn hoàn thiện biểu thức hợp lệ...")

        # --- CỘT PHẢI: TRỰC QUAN HÓA 3D (CÓ LƯỚI & SPATIAL ANCHOR) ---
        with col_plot:
            fig = go.Figure()
            
            # Tính toán không gian bao quát để vẽ mặt phẳng Oxy
            max_range = np.max(np.abs(edited_df.iloc[:, 1:].values)) if not edited_df.empty else 5.0
            max_range = max(max_range, 5.0) + 2.0
            
            # 1. SPATIAL ANCHOR: Vẽ mặt phẳng Oxy tại z=0 mờ nhạt
            x_surf = np.array([[-max_range, max_range], [-max_range, max_range]])
            y_surf = np.array([[-max_range, -max_range], [max_range, max_range]])
            z_surf = np.zeros((2, 2))
            
            fig.add_trace(go.Surface(
                x=x_surf, y=y_surf, z=z_surf,
                opacity=0.15,
                colorscale=[[0, '#007AFF'], [1, '#007AFF']],
                showscale=False,
                hoverinfo='skip',
                name='Mặt phẳng Oxy (z=0)'
            ))

            # 2. Vẽ các vector chính
            colors = ['#007AFF', '#34C759', '#5856D6', '#00C7BE', '#AF52DE']
            for i, (name, data) in enumerate(vectors.items()):
                c_color = colors[i % len(colors)]
                p_start, p_end = data['start'], data['end']
                
                # Thân vector
                fig.add_trace(go.Scatter3d(
                    x=[p_start[0], p_end[0]], y=[p_start[1], p_end[1]], z=[p_start[2], p_end[2]],
                    mode='lines', line=dict(width=6, color=c_color), showlegend=False
                ))
                # Ngọn vector
                fig.add_trace(go.Scatter3d(
                    x=[p_end[0]], y=[p_end[1]], z=[p_end[2]],
                    mode='markers+text', marker=dict(size=5, symbol='diamond', color=c_color),
                    text=[rf"<b>{name}</b>"], textposition="top center",
                    textfont=dict(size=15, color=c_color), showlegend=False
                ))

            # 3. Vẽ vector bổ sung (Kết quả tính toán)
            for trace in additional_plot_traces:
                p_start, p_end, t_color, t_name = trace['start'], trace['end'], trace['color'], trace['name']
                fig.add_trace(go.Scatter3d(
                    x=[p_start[0], p_end[0]], y=[p_start[1], p_end[1]], z=[p_start[2], p_end[2]],
                    mode='lines', line=dict(width=8, color=t_color, dash='dash'), showlegend=False
                ))
                fig.add_trace(go.Scatter3d(
                    x=[p_end[0]], y=[p_end[1]], z=[p_end[2]],
                    mode='markers+text', marker=dict(size=7, symbol='diamond', color=t_color),
                    text=[rf"<b>{t_name}</b>"], textposition="top center",
                    textfont=dict(size=15, color=t_color), showlegend=False
                ))

            # Thiết lập hiển thị trục Oxyz
            fig.update_layout(
                margin=dict(l=0, r=0, b=0, t=0),
                paper_bgcolor='rgba(0,0,0,0)',
                scene=dict(
                    aspectmode='cube', # Tỉ lệ 1:1:1 chống méo hình
                    xaxis=dict(range=[-max_range, max_range], showgrid=True, gridcolor='#E5E5EA', zeroline=True, zerolinewidth=3, zerolinecolor='#8E8E93', title="X"),
                    yaxis=dict(range=[-max_range, max_range], showgrid=True, gridcolor='#E5E5EA', zeroline=True, zerolinewidth=3, zerolinecolor='#8E8E93', title="Y"),
                    zaxis=dict(range=[-max_range, max_range], showgrid=True, gridcolor='#E5E5EA', zeroline=True, zerolinewidth=3, zerolinecolor='#8E8E93', title="Z"),
                    camera=dict(eye=dict(x=1.6, y=1.6, z=1.0))
                ),
                height=650
            )
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Lỗi hệ thống: {e}. Vui lòng kiểm tra lại dữ liệu đầu vào.")

if __name__ == "__main__":
    main()
