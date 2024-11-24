from langchain.tools import BaseTool
from typing import Optional, Type, Any
import pandas as pd
from pydantic import BaseModel, Field, ConfigDict
import matplotlib.pyplot as plt

class BasePandasTool(BaseTool):
    """Base class for pandas dataframe tools"""
    ihtiyac_df: Any = Field(default=None, exclude=True)
    norm_fazlasi_df: Any = Field(default=None, exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

class BransKarsilastirmaTool(BasePandasTool):
    name: str = "brans_karsilastirma"
    description: str = """Bu tool branşlara göre karşılaştırmalı analiz yapar.
    Her branş için ihtiyaç ve norm fazlası sayılarını karşılaştırır.
    Kullanım: Branşları karşılaştırmak istediğinizde kullanın."""
    
    def __init__(self, ihtiyac_df: pd.DataFrame, norm_fazlasi_df: pd.DataFrame, **kwargs):
        super().__init__(**kwargs)
        self.ihtiyac_df = ihtiyac_df
        self.norm_fazlasi_df = norm_fazlasi_df

    def _run(self, query: Optional[str] = None) -> str:
        try:
            # Tüm benzersiz branşları al
            all_branches = sorted(set(self.ihtiyac_df['branş'].dropna().unique())
                                .union(self.norm_fazlasi_df['Branşı'].dropna().unique()))
            
            results = []
            for brans in all_branches:
                # İhtiyaç ve norm fazlası değerlerini hesapla
                total_needs = self.ihtiyac_df[self.ihtiyac_df['branş'] == brans]['ihtiyac'].sum() \
                    if brans in self.ihtiyac_df['branş'].values else 0
                    
                mazaretli_count = self.norm_fazlasi_df[
                    (self.norm_fazlasi_df['Branşı'] == brans) & 
                    (self.norm_fazlasi_df['Açıklamalar'].notna())
                ].shape[0] if brans in self.norm_fazlasi_df['Branşı'].values else 0
                
                mazaretsiz_count = self.norm_fazlasi_df[
                    (self.norm_fazlasi_df['Branşı'] == brans) & 
                    (self.norm_fazlasi_df['Açıklamalar'].isna())
                ].shape[0] if brans in self.norm_fazlasi_df['Branşı'].values else 0
                
                # Sonuçları ekle
                results.append({
                    'Branş': brans,
                    'İhtiyaç': total_needs,
                    'Norm Fazlası (Mazaretli)': mazaretli_count,
                    'Norm Fazlası (Mazaretsiz)': mazaretsiz_count,
                    'Toplam Norm Fazlası': mazaretli_count + mazaretsiz_count
                })
            
            # Sonuçları DataFrame'e çevir ve sırala
            df_results = pd.DataFrame(results)
            df_results = df_results.sort_values('İhtiyaç', ascending=False)
            
            # Sonucu formatla
            result = "Branşlara Göre Karşılaştırmalı Analiz:\n\n"
            for _, row in df_results.iterrows():
                result += f"- {row['Branş']}:\n"
                result += f"  * İhtiyaç: {int(row['İhtiyaç'])} öğretmen\n"
                result += f"  * Norm Fazlası: {int(row['Toplam Norm Fazlası'])} öğretmen "
                result += f"({int(row['Norm Fazlası (Mazaretli)'])} mazaretli, {int(row['Norm Fazlası (Mazaretsiz)'])} mazaretsiz)\n"
            
            return result
            
        except Exception as e:
            return f"Analiz yapılırken bir hata oluştu: {str(e)}"

class IlceKarsilastirmaTool(BasePandasTool):
    name: str = "ilce_karsilastirma"
    description: str = """Bu tool ilçelere göre karşılaştırmalı analiz yapar.
    Her ilçe için ihtiyaç ve norm fazlası sayılarını karşılaştırır.
    Kullanım: İlçeleri karşılaştırmak istediğinizde kullanın."""
    
    def __init__(self, ihtiyac_df: pd.DataFrame, norm_fazlasi_df: pd.DataFrame, **kwargs):
        super().__init__(**kwargs)
        self.ihtiyac_df = ihtiyac_df
        self.norm_fazlasi_df = norm_fazlasi_df

    def _run(self, query: Optional[str] = None) -> str:
        try:
            # Tüm benzersiz ilçeleri al
            all_districts = sorted(set(self.ihtiyac_df['ilçe'].dropna().unique())
                                 .union(self.norm_fazlasi_df['İlçe Adı'].dropna().unique()))
            
            results = []
            for ilce in all_districts:
                # İhtiyaç ve norm fazlası değerlerini hesapla
                total_needs = self.ihtiyac_df[self.ihtiyac_df['ilçe'] == ilce]['ihtiyac'].sum() \
                    if ilce in self.ihtiyac_df['ilçe'].values else 0
                    
                mazaretli_count = self.norm_fazlasi_df[
                    (self.norm_fazlasi_df['İlçe Adı'] == ilce) & 
                    (self.norm_fazlasi_df['Açıklamalar'].notna())
                ].shape[0] if ilce in self.norm_fazlasi_df['İlçe Adı'].values else 0
                
                mazaretsiz_count = self.norm_fazlasi_df[
                    (self.norm_fazlasi_df['İlçe Adı'] == ilce) & 
                    (self.norm_fazlasi_df['Açıklamalar'].isna())
                ].shape[0] if ilce in self.norm_fazlasi_df['İlçe Adı'].values else 0
                
                # Sonuçları ekle
                results.append({
                    'İlçe': ilce,
                    'İhtiyaç': total_needs,
                    'Norm Fazlası (Mazaretli)': mazaretli_count,
                    'Norm Fazlası (Mazaretsiz)': mazaretsiz_count,
                    'Toplam Norm Fazlası': mazaretli_count + mazaretsiz_count
                })
            
            # Sonuçları DataFrame'e çevir ve sırala
            df_results = pd.DataFrame(results)
            df_results = df_results.sort_values('İhtiyaç', ascending=False)
            
            # Sonucu formatla
            result = "İlçelere Göre Karşılaştırmalı Analiz:\n\n"
            for _, row in df_results.iterrows():
                result += f"- {row['İlçe']}:\n"
                result += f"  * İhtiyaç: {int(row['İhtiyaç'])} öğretmen\n"
                result += f"  * Norm Fazlası: {int(row['Toplam Norm Fazlası'])} öğretmen "
                result += f"({int(row['Norm Fazlası (Mazaretli)'])} mazaretli, {int(row['Norm Fazlası (Mazaretsiz)'])} mazaretsiz)\n"
            
            return result
            
        except Exception as e:
            return f"Analiz yapılırken bir hata oluştu: {str(e)}"

class IlceBransFiltrelemeTool(BasePandasTool):
    name: str = "ilce_brans_filtreleme"
    description: str = """Bu tool belirli bir ilçedeki branşlara göre norm fazlası ve ihtiyaç analizini yapar.
    İlçe adı verilerek o ilçedeki branş bazlı durumu analiz eder.
    Kullanım: Bir ilçedeki branşlara göre durumu öğrenmek istediğinizde kullanın.
    Örnek: "Muratpaşa'da hangi branşlarda norm fazlası var?" gibi sorular için."""
    
    def __init__(self, ihtiyac_df: pd.DataFrame, norm_fazlasi_df: pd.DataFrame, **kwargs):
        super().__init__(**kwargs)
        self.ihtiyac_df = ihtiyac_df
        self.norm_fazlasi_df = norm_fazlasi_df

    def _run(self, query: Optional[str] = None) -> str:
        try:
            # Query'den ilçe adını çıkar
            ilce = None
            for potential_ilce in self.norm_fazlasi_df['İlçe Adı'].unique():
                if potential_ilce.lower() in query.lower():
                    ilce = potential_ilce
                    break
            
            if not ilce:
                return "İlçe adı bulunamadı. Lütfen geçerli bir ilçe adı belirtin."

            # İlçeye göre filtrele
            ilce_norm = self.norm_fazlasi_df[self.norm_fazlasi_df['İlçe Adı'] == ilce]
            ilce_ihtiyac = self.ihtiyac_df[self.ihtiyac_df['ilçe'] == ilce]
            
            # Branşlara göre analiz
            results = []
            
            # Norm fazlası analizi
            norm_brans_counts = ilce_norm.groupby('Branşı').agg({
                'Açıklamalar': lambda x: (x.isna().sum(), x.notna().sum())  # (mazaretsiz, mazaretli)
            }).reset_index()
            
            # İhtiyaç analizi
            ihtiyac_brans = ilce_ihtiyac.groupby('branş')['ihtiyac'].sum()
            
            # Tüm branşları birleştir
            all_branches = set(norm_brans_counts['Branşı']).union(set(ihtiyac_brans.index))
            
            for brans in all_branches:
                norm_row = norm_brans_counts[norm_brans_counts['Branşı'] == brans]
                mazaretsiz = norm_row['Açıklamalar'].iloc[0][0] if not norm_row.empty else 0
                mazaretli = norm_row['Açıklamalar'].iloc[0][1] if not norm_row.empty else 0
                ihtiyac = ihtiyac_brans.get(brans, 0)
                
                if mazaretsiz > 0 or mazaretli > 0 or ihtiyac > 0:
                    results.append({
                        'Branş': brans,
                        'Norm Fazlası (Mazaretsiz)': mazaretsiz,
                        'Norm Fazlası (Mazaretli)': mazaretli,
                        'İhtiyaç': ihtiyac
                    })
            
            # Sonuçları DataFrame'e çevir ve sırala
            df_results = pd.DataFrame(results)
            df_results['Toplam Norm Fazlası'] = df_results['Norm Fazlası (Mazaretsiz)'] + df_results['Norm Fazlası (Mazaretli)']
            df_results = df_results.sort_values('Toplam Norm Fazlası', ascending=False)
            
            # Sonucu formatla
            result = f"{ilce} İlçesi Branş Analizi:\n\n"
            
            # Norm fazlası olan branşlar
            norm_fazlasi_branslar = df_results[df_results['Toplam Norm Fazlası'] > 0]
            if not norm_fazlasi_branslar.empty:
                result += "Norm Fazlası Olan Branşlar:\n"
                for _, row in norm_fazlasi_branslar.iterrows():
                    result += f"- {row['Branş']}:\n"
                    result += f"  * Toplam: {int(row['Toplam Norm Fazlası'])} öğretmen "
                    result += f"({int(row['Norm Fazlası (Mazaretli)'])} mazaretli, {int(row['Norm Fazlası (Mazaretsiz)'])} mazaretsiz)\n"
                    if row['İhtiyaç'] > 0:
                        result += f"  * Aynı zamanda {int(row['İhtiyaç'])} öğretmen ihtiyaç var\n"
            
            # İhtiyaç olan branşlar
            ihtiyac_branslar = df_results[df_results['İhtiyaç'] > 0]
            if not ihtiyac_branslar.empty:
                result += "\nİhtiyaç Olan Branşlar:\n"
                for _, row in ihtiyac_branslar.iterrows():
                    if row['Toplam Norm Fazlası'] == 0:  # Sadece norm fazlası olmayanları listele
                        result += f"- {row['Branş']}: {int(row['İhtiyaç'])} öğretmen ihtiyaç var\n"
            
            return result
            
        except Exception as e:
            return f"Analiz yapılırken bir hata oluştu: {str(e)}" 

class IlceNormFazlasiSiralama(BasePandasTool):
    name: str = "ilce_norm_fazlasi_siralama"
    description: str = """Bu tool ilçelerdeki norm fazlası öğretmen sayılarını sıralar.
    En çok norm fazlası olan ilçeleri ve sayılarını listeler.
    Kullanım: Hangi ilçede en fazla norm fazlası öğretmen olduğunu öğrenmek istediğinizde kullanın."""
    
    def __init__(self, ihtiyac_df: pd.DataFrame, norm_fazlasi_df: pd.DataFrame, **kwargs):
        super().__init__(**kwargs)
        self.ihtiyac_df = ihtiyac_df
        self.norm_fazlasi_df = norm_fazlasi_df

    def _run(self, query: Optional[str] = None) -> str:
        try:
            # İlçelere göre norm fazlası analizi
            ilce_analiz = self.norm_fazlasi_df.groupby('İlçe Adı').agg({
                'S.N': 'count',  # Toplam norm fazlası
                'Açıklamalar': lambda x: (x.isna().sum(), x.notna().sum())  # (mazaretsiz, mazaretli)
            }).reset_index()
            
            # Sonuçları düzenle
            results = []
            for _, row in ilce_analiz.iterrows():
                mazaretsiz, mazaretli = row['Açıklamalar']
                toplam = row['S.N']
                
                results.append({
                    'İlçe': row['İlçe Adı'],
                    'Toplam Norm Fazlası': toplam,
                    'Mazaretli': mazaretli,
                    'Mazaretsiz': mazaretsiz
                })
            
            # DataFrame oluştur ve sırala
            df_results = pd.DataFrame(results)
            df_results = df_results.sort_values('Toplam Norm Fazlası', ascending=False)
            
            # Sonucu formatla
            result = "İlçelere Göre Norm Fazlası Öğretmen Sayıları:\n\n"
            
            # En yüksek norm fazlası olan ilçeyi vurgula
            en_yuksek = df_results.iloc[0]
            result += f"🔴 En fazla norm fazlası {en_yuksek['İlçe']} ilçesinde:\n"
            result += f"   * Toplam: {int(en_yuksek['Toplam Norm Fazlası'])} öğretmen\n"
            result += f"   * Mazaretli: {int(en_yuksek['Mazaretli'])} öğretmen\n"
            result += f"   * Mazaretsiz: {int(en_yuksek['Mazaretsiz'])} öğretmen\n\n"
            
            # Diğer ilçeleri listele
            result += "Diğer İlçelerin Durumu:\n"
            for _, row in df_results.iloc[1:].iterrows():
                result += f"- {row['İlçe']}: {int(row['Toplam Norm Fazlası'])} öğretmen "
                result += f"({int(row['Mazaretli'])} mazaretli, {int(row['Mazaretsiz'])} mazaretsiz)\n"
            
            # İstatistiksel özet
            toplam_norm_fazlasi = df_results['Toplam Norm Fazlası'].sum()
            toplam_mazaretli = df_results['Mazaretli'].sum()
            toplam_mazaretsiz = df_results['Mazaretsiz'].sum()
            
            result += f"\nGenel Durum:\n"
            result += f"* Toplam Norm Fazlası: {int(toplam_norm_fazlasi)} öğretmen\n"
            result += f"* Toplam Mazaretli: {int(toplam_mazaretli)} öğretmen\n"
            result += f"* Toplam Mazaretsiz: {int(toplam_mazaretsiz)} öğretmen"
            
            return result
            
        except Exception as e:
            return f"Analiz yapılırken bir hata oluştu: {str(e)}" 