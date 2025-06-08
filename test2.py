import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

### 🔵CSV読み込み
kouza = pd.read_csv('kouza.csv', encoding="utf-8")
kokyaku = pd.read_csv('kokyaku.csv', encoding="utf-8")
torihiki = pd.read_csv('torihiki.csv', encoding="utf-8")
torihiki_1 = pd.read_csv('torihiki_1.csv', encoding="utf-8")



###  🟡アプリ画面設定
# アプリ画面をwideモードで設定
st.set_page_config(page_title='testapp', page_icon='💹', layout='wide')

# 背景色変更
st.markdown('<style>.stApp {background-color: #FAFAD2;}</style>', unsafe_allow_html=True)

# 日本語フォント設定
plt.rcParams['font.family'] = 'Noto Sans JP'
sns.set(style='darkgrid', font_scale=1.2)


### 🔴 CSV取込みテスト画面
tab1, tab2 = st.tabs(['📑 CSV取込みテスト', '🔍 データフィルタリングテスト'])
with tab1:
    st.markdown("<h2 style='color: #E67E22;'>📑 CSV取込みテスト</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 4])
    with col1:
        # セレクトボックス設定（選択可能な月をデータから動的に取得）
        options = sorted(kouza['date'].str[:7].unique(), reverse=True) #「2025-03」等(7文字)取得
        selected_month_str = st.selectbox('表示月を選択', options, key='month_select', label_visibility='collapsed') 
        selected_month = pd.to_datetime(selected_month_str)

    # フィルタリングのための日付変換
    kouza['date'] = pd.to_datetime(kouza['date']).dt.strftime('%Y-%m-%d')
    filtered_data = kouza[kouza['date'].str.startswith(selected_month.strftime('%Y-%m'))].reset_index(drop=True)
    filtered_data.index += 1

    col3, col4 = st.columns(2)
    # 口座数データ表示
    with col3:
        st.markdown("<p style='font-size:16px; color:gray; font-weight:bold;'>日次口座数</p>", unsafe_allow_html=True)
        st.dataframe(filtered_data, height=min(filtered_data.shape[0] * 35, 300)) 
    # 口座推移の折れ線グラフ表示
    with col4:
        st.markdown('<p style="font-size:16px; color:gray; font-weight:bold;">口座数推移</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor('#FAFAD2')
        ax.plot(filtered_data['date'], filtered_data['kouza'], label='実績')
        ax.plot(filtered_data['date'], filtered_data['goal'], label='目標')
        ax.set_xticks(filtered_data['date'][::10])
        ax.set_xlabel('日付')
        ax.set_ylabel('口座数')
        ax.legend()
        st.pyplot(fig)

    col5, col6 = st.columns(2)
    # 年齢別残高割合円グラフ作成の前処理                       
    bins = [20, 30, 40, 50, 60, 70, 80, 90]
    labels = ['20代', '30代', '40代', '50代', '60代', '70代', '80代']
    cut = pd.cut(kokyaku['age'], bins=bins, labels=labels, right=False)
    value_counts = cut.value_counts(sort=False)
    light_colors = ['#FFC1CC', '#FFDDC1', '#D1FFC1', '#C1D9FF', '#E1C1FF', '#FFE1DD', '#FFFFC1']
    # 年齢別残高割合円グラフ表示
    with col5:
        st.markdown('<p style="font-size:16px; color:gray; font-weight:bold;">年齢別残高割合</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots()
        fig.patch.set_facecolor('#FAFAD2')
        ax.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=90, colors=light_colors)
        ax.axis('equal')
        st.pyplot(fig) 

    # 商品売買額の棒グラフ表示
    torihiki.loc[torihiki['buysell'] == '売', 'total'] *= -1
    with col6:
        st.markdown('<p style="font-size:16px; color:gray; font-weight:bold;">商品別売買額</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots()
        fig.patch.set_facecolor('#FAFAD2')
        ax.bar(
            torihiki['product'],
            torihiki['total'],
            color=['#ADD8E6' if v > 0 else '#FFB6C1' for v in torihiki['total']]
        )
        ax.axhline(0, color="black", linewidth=1)
        ax.set_ylabel("売買額")
        st.pyplot(fig) 


### 🟤 データフィルタリングテスト
with tab2:
    st.markdown("<h2 style='color: #0066ff;'>🔍 データフィルタリングテスト</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # 日付を文字列 → 日付型に変換し、ソート
        torihiki_1['date'] = pd.to_datetime(torihiki_1['date']).dt.date
        torihiki_1 = torihiki_1.sort_values('date')

        # フィルタリングの日付範囲
        start_date = max(torihiki_1['date'].min(), datetime.date(2025, 3, 1))
        end_date = min(torihiki_1['date'].max(), datetime.date(2025, 5, 31))

        # 日付範囲選択
        selected_dates = st.date_input('範囲を選択', (start_date, end_date), min_value=start_date, max_value=end_date)

        # **カスタムCSS適用**
        st.markdown("""
            <style>
            span[data-baseweb="tag"] {
                background-color: #007BFF !important;  /* 青色 */
                color: white !important;  /* 文字色を白に */
            }
            </style>
        """, unsafe_allow_html=True)

        # **商品と銘柄の選択枠を横並びに配置**
        col1, col2 = st.columns(2)

        # `product` の選択肢
        with col1:
            selected_products = st.multiselect('商品を選択', torihiki_1['product'].unique(), default=torihiki_1['product'].unique())

        # `selected_products` に応じて `meigara` の選択肢を動的に変更
        filtered_meigara = torihiki_1.loc[torihiki_1['product'].isin(selected_products), 'meigara'].unique()

        # `meigara` の選択肢
        with col2:
            selected_meigara = st.multiselect('銘柄を選択', filtered_meigara, default=filtered_meigara)

        # `buysell` の選択肢
        selected_buysell = st.multiselect('売買区分を選択', torihiki_1['buysell'].unique(), default=torihiki_1['buysell'].unique())

        # **total の範囲選択（1000円単位）**
        total_min, total_max = [0, torihiki_1['total'].max()]

        selected_total_range = st.slider(
            '金額の範囲を選択',
            min_value=total_min,
            max_value=total_max,
            value=(total_min, total_max),
            step=1000
        )

        # データフィルタリング
        torihiki_1_filtered = torihiki_1[
            (torihiki_1['date'] >= selected_dates[0]) & (torihiki_1['date'] <= selected_dates[1]) &
            (torihiki_1['product'].isin(selected_products)) &
            (torihiki_1['buysell'].isin(selected_buysell)) &
            (torihiki_1['meigara'].isin(selected_meigara)) &
            (torihiki_1['total'].between(selected_total_range[0], selected_total_range[1]))
        ]

        # **インデックスをリセット**
        torihiki_1_filtered.reset_index(drop=True, inplace=True)
        torihiki_1_filtered.index = torihiki_1_filtered.index + 1

        # フィルタ後のデータ表示（高さ固定）
        st.data_editor(torihiki_1_filtered, height=600, use_container_width=True)
