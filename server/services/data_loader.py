import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self):
        self.data_dir = Path("data")
        try:
            self._load_data()
        except ImportError as e:
            logger.error(f"Gerekli paket eksik: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Veri yüklenirken hata oluştu: {str(e)}")
            raise

    def _load_data(self):
        """Load Excel files and convert them to DataFrames"""
        try:
            # Excel dosyalarının var olduğunu kontrol et
            ihtiyac_path = self.data_dir / "ihtiyac_data.xlsx"
            norm_fazlasi_path = self.data_dir / "norm_fazlasi.xlsx"

            if not ihtiyac_path.exists():
                raise FileNotFoundError(f"Dosya bulunamadı: {ihtiyac_path}")
            if not norm_fazlasi_path.exists():
                raise FileNotFoundError(f"Dosya bulunamadı: {norm_fazlasi_path}")

            # Dosyaları oku
            self.ihtiyac_df = pd.read_excel(ihtiyac_path)
            self.norm_fazlasi_df = pd.read_excel(norm_fazlasi_path)
            
            # Cache common analytics
            self._cache_analytics()
            
        except Exception as e:
            logger.error(f"Veri yüklenirken hata oluştu: {str(e)}")
            raise

    def _cache_analytics(self):
        """Pre-calculate common analytics for faster responses"""
        try:
            # İhtiyaç analizi
            self.branş_ihtiyac = self.ihtiyac_df.groupby('branş')['ihtiyac'].sum().sort_values(ascending=False)
            
            # Norm fazlası analizi  
            self.ilce_norm_fazlasi = self.norm_fazlasi_df.groupby('İlçe Adı')['S.N'].count()
            
            # Top 5 ihtiyaç duyulan branşlar
            self.top_5_ihtiyac = self.branş_ihtiyac.head()
            
        except Exception as e:
            logger.error(f"Analiz hesaplanırken hata oluştu: {str(e)}")
            raise

    def get_analytics(self):
        """Return cached analytics"""
        return {
            "branş_ihtiyac": self.branş_ihtiyac.to_dict(),
            "ilce_norm_fazlasi": self.ilce_norm_fazlasi.to_dict(),
            "top_5_ihtiyac": self.top_5_ihtiyac.to_dict()
        } 