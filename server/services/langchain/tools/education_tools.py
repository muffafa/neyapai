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