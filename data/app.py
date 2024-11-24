import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt
import os

# Load the Excel files
df_norm = pd.read_excel('norm_fazlasi.xlsx')
df_ihtiyac = pd.read_excel('ihtiyac_data.xlsx')

# Filter the DataFrame based on user input
def filter_dataframe(ilce_values, brans_values, aciklama_values, include_empty_aciklama):
    df = df_norm.copy()
    
    # Apply filters if values are provided
    if ilce_values and "Tüm İlçeler" not in ilce_values:
        df = df[df['İlçe Adı'].isin(ilce_values)]
    if brans_values:
        df = df[df['Branşı'].isin(brans_values)]
    if aciklama_values:
        df = df[df['Açıklamalar'].isin(aciklama_values)]
    if include_empty_aciklama:
        df = pd.concat([df, df[df['Açıklamalar'].isna()]]).drop_duplicates()
    
    return df, f"Kayıt Sayısı: {len(df)}"

# Calculate needs and norm excess per district
def calculate_needs_and_norm(ilce_values, brans_values):
    # İlçe ve branş filtreleme işlemi
    df_ihtiyac_filtered = df_ihtiyac.copy()
    df_norm_filtered = df_norm.copy()
    
    if ilce_values and "Tüm İlçeler" not in ilce_values:
        df_ihtiyac_filtered = df_ihtiyac_filtered[df_ihtiyac_filtered['ilçe'].isin(ilce_values)]
    if brans_values:
        df_ihtiyac_filtered = df_ihtiyac_filtered[df_ihtiyac_filtered['branş'].isin(brans_values)]
    
    # Özet bilgi için toplam ihtiyaç sayısını direkt olarak hesaplama
    total_needs_sum = df_ihtiyac_filtered['ihtiyac'].sum()

    # Sonuçları toplamak için liste
    results = []
    unique_ilce_values = ilce_values if ilce_values and "Tüm İlçeler" not in ilce_values else df_norm['İlçe Adı'].unique().tolist()
    unique_brans_values = brans_values if brans_values else df_norm['Branşı'].unique().tolist()

    for ilce in unique_ilce_values:
        df_norm_ilce = df_norm_filtered[df_norm_filtered['İlçe Adı'] == ilce]
        
        for brans in unique_brans_values:
            # Her ilçe ve branş için ilgili ihtiyaç miktarını hesapla
            total_needs = df_ihtiyac_filtered[(df_ihtiyac_filtered['ilçe'] == ilce) & (df_ihtiyac_filtered['branş'] == brans)]['ihtiyac'].sum()
            mazaretli_count = df_norm_ilce[(df_norm_ilce['Branşı'] == brans) & (df_norm_ilce['Açıklamalar'].notna())].shape[0]
            mazaretsiz_count = df_norm_ilce[(df_norm_ilce['Branşı'] == brans) & (df_norm_ilce['Açıklamalar'].isna())].shape[0]
            
            results.append({
                'İlçe': ilce,
                'Branş': brans,
                'Toplam İhtiyaç': total_needs,  # Her ilçe ve branşa özgü toplam ihtiyaç
                'Norm Fazlası (Mazaretli)': mazaretli_count,
                'Norm Fazlası (Mazaretsiz)': mazaretsiz_count
            })

    result_df = pd.DataFrame(results)
    total_mazaretli_sum = result_df['Norm Fazlası (Mazaretli)'].sum()
    total_mazaretsiz_sum = result_df['Norm Fazlası (Mazaretsiz)'].sum()
    
    summary_text = (f"Toplam İhtiyaç: {total_needs_sum} | "
                    f"Toplam Norm Fazlası (Mazaretli): {total_mazaretli_sum} | "
                    f"Toplam Norm Fazlası (Mazaretsiz): {total_mazaretsiz_sum}")
    
    return result_df, summary_text


# Function to plot the results as a bar chart
def plot_results(df):
    plt.figure(figsize=(14, 8))  # Grafik boyutunu artırıyoruz
    df.groupby('İlçe')[['Toplam İhtiyaç', 'Norm Fazlası (Mazaretli)', 'Norm Fazlası (Mazaretsiz)']].sum().plot(kind='bar')
    plt.title("İhtiyaç ve Norm Fazlası Dağılımı")
    plt.xlabel("İlçe")
    plt.ylabel("Sayı")
    plt.xticks(rotation=45, ha="right")  # Etiketleri biraz sağa yatırıyoruz
    plt.tight_layout()
    chart_path = 'bar_chart.png'
    plt.savefig(chart_path)
    return chart_path  # Dosya yolunu döndür

# Function to filter "ihtiyac" data based on selected ilce and brans
def filter_ihtiyac_data(ilce_values, brans_values, include_empty_aciklama=False):
    df_filtered = df_ihtiyac.copy()
    
    if ilce_values and "Tüm İlçeler" not in ilce_values:
        df_filtered = df_filtered[df_filtered['ilçe'].isin(ilce_values)]
    if brans_values:
        df_filtered = df_filtered[df_filtered['branş'].isin(brans_values)]
    
    if include_empty_aciklama:
        df_filtered = pd.concat([df_filtered, df_filtered[df_filtered['Açıklamalar'].isna()]]).drop_duplicates()
    
    total_needs_sum = df_filtered['ihtiyac'].sum()
    return df_filtered, f"Toplam İhtiyaç: {total_needs_sum}"

# Define Gradio interface components
with gr.Blocks() as demo:
    with gr.Tab("Antalya Norm Fazlası Öğretmenler"):
        ilce_choices = sorted(df_norm['İlçe Adı'].dropna().astype(str).unique().tolist())
        ilce_multiselect = gr.Dropdown(choices=["Tüm İlçeler"] + ilce_choices, label="Select İlçe Adı", multiselect=True)
        brans_multiselect = gr.Dropdown(choices=sorted(df_norm['Branşı'].dropna().unique().tolist()), label="Select Branşı", multiselect=True)
        aciklama_choices = sorted(df_norm['Açıklamalar'].dropna().unique().tolist())
        aciklama_multiselect = gr.Dropdown(choices=aciklama_choices, label="Mazaretliler", multiselect=True)
        include_empty_aciklama = gr.Checkbox(label="Mazaretsizleri de ekle")
        
        filter_button = gr.Button("Listele")
        
        record_count = gr.Textbox(label="Kişi Sayısı", interactive=False)
        output = gr.DataFrame()
        filter_button.click(fn=filter_dataframe, inputs=[ilce_multiselect, brans_multiselect, aciklama_multiselect, include_empty_aciklama], outputs=[output, record_count])
    
    with gr.Tab("İhtiyaç ve Norm Fazlası Analizi"):
        ilce_choices_ihtiyac = sorted(df_ihtiyac['ilçe'].dropna().astype(str).unique().tolist())
        ilce_multiselect_ihtiyac = gr.Dropdown(choices=["Tüm İlçeler"] + ilce_choices_ihtiyac, label="Select İlçe Adı", multiselect=True)
        brans_multiselect_ihtiyac = gr.Dropdown(choices=sorted(df_ihtiyac['branş'].dropna().unique().tolist()), label="Select Branşı", multiselect=True)
        
        analyze_button = gr.Button("Analiz Et")
        analysis_chart = gr.Image()
        analysis_record_count = gr.Textbox(label="Özet Bilgi", interactive=False)
        analysis_output = gr.DataFrame()
        
        def analyze_and_plot(ilce_values, brans_values):
            result_df, summary_text = calculate_needs_and_norm(ilce_values, brans_values)
            chart_path = plot_results(result_df)
            return result_df, summary_text, chart_path
        
        analyze_button.click(fn=analyze_and_plot, inputs=[ilce_multiselect_ihtiyac, brans_multiselect_ihtiyac], outputs=[analysis_output, analysis_record_count, analysis_chart])

    with gr.Tab("İhtiyaç Verisi Filtreleme"):
        ilce_multiselect_ihtiyac_filter = gr.Dropdown(choices=["Tüm İlçeler"] + ilce_choices_ihtiyac, label="İlçe Adı", multiselect=True)
        brans_multiselect_ihtiyac_filter = gr.Dropdown(choices=sorted(df_ihtiyac['branş'].dropna().unique().tolist()), label="Branş", multiselect=True)
        
        filter_ihtiyac_button = gr.Button("Filtrele")
        
        ihtiyac_total_count = gr.Textbox(label="Toplam İhtiyaç", interactive=False)
        ihtiyac_output = gr.DataFrame()
        
        filter_ihtiyac_button.click(fn=filter_ihtiyac_data, inputs=[ilce_multiselect_ihtiyac_filter, brans_multiselect_ihtiyac_filter], outputs=[ihtiyac_output, ihtiyac_total_count])
        
        # 4. Tab: Branşları Karşılaştırma
    # 4. Tab: Branşları Karşılaştırma
    with gr.Tab("Branşları Karşılaştırma"):
        # İhtiyaç ve norm fazlası veri çerçevelerinde bulunan tüm benzersiz branşları alıyoruz
        all_branches = sorted(set(df_ihtiyac['branş'].dropna().unique()).union(df_norm['Branşı'].dropna().unique()))
        brans_multiselect_compare = gr.Dropdown(choices=all_branches, label="Karşılaştırılacak Branşları Seçin", multiselect=True)
        
        compare_button = gr.Button("Karşılaştır")
        compare_output = gr.DataFrame()
        compare_chart = gr.Image()

        def compare_branches(brans_values):
            # Seçim yapılmadıysa tüm branşları al
            selected_branches = brans_values if brans_values else all_branches
            
            # Sonuçları toplamak için liste
            results = []
            for brans in selected_branches:
                # İlgili branş için toplam ihtiyaç ve norm fazlası değerlerini al
                total_needs = df_ihtiyac[df_ihtiyac['branş'] == brans]['ihtiyac'].sum() if brans in df_ihtiyac['branş'].values else 0
                mazaretli_count = df_norm[(df_norm['Branşı'] == brans) & (df_norm['Açıklamalar'].notna())].shape[0] if brans in df_norm['Branşı'].values else 0
                mazaretsiz_count = df_norm[(df_norm['Branşı'] == brans) & (df_norm['Açıklamalar'].isna())].shape[0] if brans in df_norm['Branşı'].values else 0
                
                # Oran hesaplaması, sıfıra bölme hatasından kaçınmak için kontrol
                if total_needs > 0:
                    ratio = (mazaretli_count + mazaretsiz_count) / total_needs
                else:
                    ratio = float('nan')  # Toplam ihtiyaç 0 ise oranı NaN olarak ayarla
                
                results.append({
                    'Branş': brans,
                    'Toplam İhtiyaç': total_needs,
                    'Norm Fazlası (Mazaretli)': mazaretli_count,
                    'Norm Fazlası (Mazaretsiz)': mazaretsiz_count,
                    'Oran': ratio
                })
            
            # Sonuçları DataFrame olarak döndür
            compare_df = pd.DataFrame(results)

            # Branş sayısı 10'dan fazlaysa grafik çizdirme
            if len(selected_branches) <= 10:
                # Çubuk grafik oluşturma
                fig, ax1 = plt.subplots(figsize=(10, 6))
                
                # İhtiyaç ve norm fazlası verilerini çubuk grafik olarak çiz
                compare_df.set_index('Branş')[['Toplam İhtiyaç', 'Norm Fazlası (Mazaretli)', 'Norm Fazlası (Mazaretsiz)']].plot(kind='bar', ax=ax1)
                ax1.set_ylabel("Sayı")
                ax1.set_xlabel("Branş")
                ax1.set_title("Branş Bazında İhtiyaç, Norm Fazlası ve Oran Karşılaştırması")
                plt.xticks(rotation=45, ha="right")
                
                # Oran verilerini ikincil bir eksen olarak çiz
                ax2 = ax1.twinx()
                ax2.plot(compare_df['Branş'], compare_df['Oran'], color='red', marker='o', linestyle='-', linewidth=2)
                ax2.set_ylabel("Oran", color='red')
                ax2.tick_params(axis='y', labelcolor='red')
                
                plt.tight_layout()
                chart_path = 'branch_comparison_chart.png'
                plt.savefig(chart_path)
                plt.close()
            else:
                chart_path = None  # Grafik gösterilmeyecek
            
            return compare_df, chart_path

        compare_button.click(fn=compare_branches, inputs=[brans_multiselect_compare], outputs=[compare_output, compare_chart])
    # 5. Tab: İlçeleri Karşılaştırma
    with gr.Tab("İlçeleri Karşılaştırma"):
        # İhtiyaç ve norm fazlası veri çerçevelerinde bulunan tüm benzersiz ilçeleri alıyoruz
        all_districts = sorted(set(df_ihtiyac['ilçe'].dropna().unique()).union(df_norm['İlçe Adı'].dropna().unique()))
        ilce_multiselect_compare = gr.Dropdown(choices=all_districts, label="Karşılaştırılacak İlçeleri Seçin", multiselect=True)
        
        compare_button_ilce = gr.Button("Karşılaştır")
        compare_output_ilce = gr.DataFrame()
        compare_chart_ilce = gr.Image()

        def compare_districts(ilce_values):
            # Seçim yapılmadıysa tüm ilçeleri al
            selected_districts = ilce_values if ilce_values else all_districts
            
            # Sonuçları toplamak için liste
            results = []
            for ilce in selected_districts:
                # İlgili ilçe için toplam ihtiyaç ve norm fazlası değerlerini al
                total_needs = df_ihtiyac[df_ihtiyac['ilçe'] == ilce]['ihtiyac'].sum() if ilce in df_ihtiyac['ilçe'].values else 0
                mazaretli_count = df_norm[(df_norm['İlçe Adı'] == ilce) & (df_norm['Açıklamalar'].notna())].shape[0] if ilce in df_norm['İlçe Adı'].values else 0
                mazaretsiz_count = df_norm[(df_norm['İlçe Adı'] == ilce) & (df_norm['Açıklamalar'].isna())].shape[0] if ilce in df_norm['İlçe Adı'].values else 0
                
                # Oran hesaplaması, sıfıra bölme hatasından kaçınmak için kontrol
                if total_needs > 0:
                    ratio = (mazaretli_count + mazaretsiz_count) / total_needs
                else:
                    ratio = float('nan')  # Toplam ihtiyaç 0 ise oranı NaN olarak ayarla
                
                results.append({
                    'İlçe': ilce,
                    'Toplam İhtiyaç': total_needs,
                    'Norm Fazlası (Mazaretli)': mazaretli_count,
                    'Norm Fazlası (Mazaretsiz)': mazaretsiz_count,
                    'Oran': ratio
                })
            
            # Sonuçları DataFrame olarak döndür
            compare_df_ilce = pd.DataFrame(results)

            # İlçe sayısı 10'dan fazlaysa grafik çizdirme
            if len(selected_districts) <= 10:
                # Çubuk grafik oluşturma
                fig, ax1 = plt.subplots(figsize=(10, 6))
                
                # İhtiyaç ve norm fazlası verilerini çubuk grafik olarak çiz
                compare_df_ilce.set_index('İlçe')[['Toplam İhtiyaç', 'Norm Fazlası (Mazaretli)', 'Norm Fazlası (Mazaretsiz)']].plot(kind='bar', ax=ax1)
                ax1.set_ylabel("Sayı")
                ax1.set_xlabel("İlçe")
                ax1.set_title("İlçe Bazında İhtiyaç, Norm Fazlası ve Oran Karşılaştırması")
                plt.xticks(rotation=45, ha="right")
                
                # Oran verilerini ikincil bir eksen olarak çiz
                ax2 = ax1.twinx()
                ax2.plot(compare_df_ilce['İlçe'], compare_df_ilce['Oran'], color='red', marker='o', linestyle='-', linewidth=2)
                ax2.set_ylabel("Oran", color='red')
                ax2.tick_params(axis='y', labelcolor='red')
                
                plt.tight_layout()
                chart_path_ilce = 'district_comparison_chart.png'
                plt.savefig(chart_path_ilce)
                plt.close()
            else:
                chart_path_ilce = None  # Grafik gösterilmeyecek
            
            return compare_df_ilce, chart_path_ilce

        compare_button_ilce.click(fn=compare_districts, inputs=[ilce_multiselect_compare], outputs=[compare_output_ilce, compare_chart_ilce])

# Run the app
demo.launch()
