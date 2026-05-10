import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math

# ==========================================
# 1. CẤU HÌNH TRANG & CSS (CHUẨN ED-ODYSSEY)
# ==========================================
st.set_page_config(page_title="ED-ODYSSEY | Vector Lab", layout="wide", page_icon="🎯")

def inject_custom_css():
    st.markdown("""
    <style>
    /* Nền trang Minimalist */
    .stApp { background-color: #F4F7FA; font-family: 'Inter', sans-serif; }
    
    /* Container bo góc 20px, bóng đổ Neumorphism */
    div[data-testid="stVerticalBlock"] > div {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        border: 1px solid #E9ECEF;
        margin-bottom: 15px;
    }

    /* Hiệu ứng Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        border-right: 1px solid #E9ECEF;
    }

    .sidebar-title {
        font-size: 1.5rem; font-weight: 800; color: #007AFF; text-align: center; margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. HÀM HỖ TRỢ PLOTLY THEME
# ==========================================
def get_plotly_layout(title=""):
    return dict(
        title=title,
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#111827'),
        xaxis=dict(showgrid=True, gridcolor='#E5E7EB', zerolinecolor='#9CA3AF', zerolinewidth=2),
        yaxis=dict(showgrid=True, gridcolor='#E5E7EB', zerolinecolor='#9CA3AF', zerolinewidth=2, scaleanchor="x", scaleratio=1),
        margin=dict(l=20, r=20, t=40, b=20)
    )

def draw_vector(fig, x0, y0, x1, y1, name, color, dash="solid", width=3):
    """Hàm vẽ mũi tên vector trên Plotly"""
    fig.add_annotation(
        x=x1, y=y1, ax=x0, ay=y0,
        xref='x', yref='y', axref='x', ayref='y',
        text='', showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=width, arrowcolor=color
    )
    # Vẽ thân vector (để hỗ trợ nét đứt nếu cần)
    fig.add_trace(go.Scatter(
        x=[x0, x1], y=[y0, y1], mode='lines', line=dict(color=color, width=width, dash=dash), showlegend=False, hoverinfo="skip"
    ))
    # Nhãn tên
    fig.add_trace(go.Scatter(
        x=[(x0+x1)/2], y=[(y0+y1)/2], mode='text', text=[f"<b>{name}</b>"], textfont=dict(color=color, size=14), textposition="top center", showlegend=False
    ))

# ==========================================
# 3. QUẢN LÝ TRẠNG THÁI & GIAO DIỆN
# ==========================================
inject_custom_css()

if 'vec_df' not in st.session_state:
    st.session_state.vec_df = pd.DataFrame({
        "Tên Vector": ["u", "v", "w"],
        "x_Đầu": [0.0, 1.0, -2.0],
        "y_Đầu": [0.0, 2.0, 4.0],
        "x_Cuối": [3.0, 4.0, 1.0],
        "y_Cuối": [2.0, 6.0, 6.0]
    })

with st.sidebar:
    st.markdown('<div class="sidebar-title">🛡️ ED-ODYSSEY</div>', unsafe_allow_html=True)
    st.markdown("**Module: Tương Tác Vector**")
    st.divider()
    menu = st.radio("CHỌN TÍNH NĂNG:", ["1. Tích Vô Hướng & Góc", "2. Cộng Vector (Quy Tắc Đa Giác)"])
    st.divider()
    st.info("Chỉnh sửa trực tiếp tọa độ trong bảng Data Editor.")

st.subheader("📝 Không Gian Nhập Liệu (n-Vector)")
edited_df = st.data_editor(st.session_state.vec_df, num_rows="dynamic", use_container_width=True, hide_index=True)

# Lọc bỏ các hàng rỗng
valid_df = edited_df.dropna(subset=["Tên Vector", "x_Đầu", "y_Đầu", "x_Cuối", "y_Cuối"]).copy()
valid_df["dx"] = valid_df["x_Cuối"] - valid_df["x_Đầu"]
valid_df["dy"] = valid_df["y_Cuối"] - valid_df["y_Đầu"]

vec_names = valid_df["Tên Vector"].tolist()
colors = ['#007AFF', '#34C759', '#FF9500', '#AF52DE', '#5856D6']

# ==========================================
# CHẾ ĐỘ 1: TÍCH VÔ HƯỚNG & ĐỘ LỚN
# ==========================================
if menu.startswith("1"):
    col_calc, col_plot = st.columns([1, 1.5])
    
    with col_calc:
        st.markdown("### 🧮 Tích Vô Hướng (Dot Product)")
        if len(vec_names) >= 2:
            v1_name = st.selectbox("Chọn Vector thứ nhất:", vec_names, index=0)
            v2_name = st.selectbox("Chọn Vector thứ hai:", vec_names, index=1)
            
            v1 = valid_df[valid_df["Tên Vector"] == v1_name].iloc[0]
            v2 = valid_df[valid_df["Tên Vector"] == v2_name].iloc[0]
            
            vec1 = np.array([v1["dx"], v1["dy"]])
            vec2 = np.array([v2["dx"], v2["dy"]])
            
            dot_prod = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            cos_theta = dot_prod / (norm1 * norm2) if (norm1*norm2) > 0 else 0
            cos_theta = max(min(cos_theta, 1.0), -1.0) # Tránh lỗi float
            angle_deg = math.degrees(math.acos(cos_theta))
            
            st.latex(rf"\vec{{{v1_name}}} = ({vec1[0]:.1f}; {vec1[1]:.1f}) \quad \vec{{{v2_name}}} = ({vec2[0]:.1f}; {vec2[1]:.1f})")
            st.latex(rf"\vec{{{v1_name}}} \cdot \vec{{{v2_name}}} = {dot_prod:.2f}")
            st.latex(rf"|\vec{{{v1_name}}}| = {norm1:.2f} \quad |\vec{{{v2_name}}}| = {norm2:.2f}")
            st.latex(rf"\cos \theta = {cos_theta:.3f} \implies \theta \approx {angle_deg:.1f}^\circ")
        else:
            st.warning("Cần ít nhất 2 vector để thực hiện phép tính.")

    with col_plot:
        fig = go.Figure()
        max_limit = 5
        for i, row in valid_df.iterrows():
            draw_vector(fig, row["x_Đầu"], row["y_Đầu"], row["x_Cuối"], row["y_Cuối"], row["Tên Vector"], colors[i % len(colors)])
            max_limit = max(max_limit, abs(row["x_Đầu"]), abs(row["x_Cuối"]), abs(row["y_Đầu"]), abs(row["y_Cuối"]))
        
        fig.update_layout(get_plotly_layout("Trực quan Không gian Vector"))
        fig.update_xaxes(range=[-max_limit-1, max_limit+1])
        fig.update_yaxes(range=[-max_limit-1, max_limit+1])
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# CHẾ ĐỘ 2: PHÉP CỘNG VECTOR (QUY TẮC ĐA GIÁC)
# ==========================================
elif menu.startswith("2"):
    col_calc, col_plot = st.columns([1, 1.5])
    
    with col_calc:
        st.markdown("### 🔗 Phép Cộng Nối Đuôi")
        st.write("Chọn thứ tự các vector muốn cộng. Hệ thống sẽ tự động tịnh tiến chúng.")
        selected_vecs = st.multiselect("Thứ tự cộng (Ví dụ: u + v + w):", vec_names, default=vec_names)
        
        if selected_vecs:
            # Lấy điểm xuất phát là điểm đầu của vector đầu tiên trong chuỗi
            start_v = valid_df[valid_df["Tên Vector"] == selected_vecs[0]].iloc[0]
            start_x, start_y = start_v["x_Đầu"], start_v["y_Đầu"]
            
            sum_dx, sum_dy = 0.0, 0.0
            latex_sum = " + ".join([rf"\vec{{{name}}}" for name in selected_vecs])
            
            for name in selected_vecs:
                v = valid_df[valid_df["Tên Vector"] == name].iloc[0]
                sum_dx += v["dx"]
                sum_dy += v["dy"]
                
            norm_sum = math.hypot(sum_dx, sum_dy)
            
            st.success("Đã tính xong Vector Tổng!")
            st.latex(rf"\vec{{Tổng}} = {latex_sum} = ({sum_dx:.1f}; {sum_dy:.1f})")
            st.latex(rf"|\vec{{Tổng}}| = \sqrt{{{sum_dx:.1f}^2 + {sum_dy:.1f}^2}} = {norm_sum:.2f}")

    with col_plot:
        fig = go.Figure()
        if selected_vecs:
            curr_x, curr_y = start_x, start_y
            max_limit = max(abs(start_x), abs(start_y))
            
            # Vẽ các vector thành phần (tịnh tiến nối đuôi)
            for i, name in enumerate(selected_vecs):
                v = valid_df[valid_df["Tên Vector"] == name].iloc[0]
                next_x = curr_x + v["dx"]
                next_y = curr_y + v["dy"]
                
                draw_vector(fig, curr_x, curr_y, next_x, next_y, name, colors[i % len(colors)])
                max_limit = max(max_limit, abs(next_x), abs(next_y))
                
                curr_x, curr_y = next_x, next_y
            
            # Vẽ VECTOR TỔNG (Màu đỏ, nét đứt)
            draw_vector(fig, start_x, start_y, curr_x, curr_y, "Tổng", "#FF3B30", dash="dash", width=4)
            
            fig.update_layout(get_plotly_layout("Quy tắc Đa giác (Nối đuôi)"))
            fig.update_xaxes(range=[-max_limit-2, max_limit+2])
            fig.update_yaxes(range=[-max_limit-2, max_limit+2])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Vui lòng chọn ít nhất 1 vector để vẽ.")
