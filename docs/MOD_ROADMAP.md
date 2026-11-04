# Mod geliştirme ilerleme haritası

Bu tur mevcut HMOD API 0.2 özelliklerini kullanılabilir örneklerle sunar. Modpack,
script sistemi ve daha gelişmiş mod API'leri sonraki tura aittir.

| Sıra | Teslim | Örnek mod | Oyun içi kabul kontrolü |
|---|---|---|---|
| 1 | Manifest, namespace, yaratıcı sekmesi, kaynak oluşturma aracı | copper-tools | Üç alet sekmede ve `/give` ile görünür |
| 2 | Template davranışı, tekli yığın, dayanıklılık bileşeni | miner-kit | Kazma kullanıldıkça, miğfer hasar aldıkça dayanıklılık azalır |
| 3 | Şekilli üretim, fırında geri dönüşüm | copper-processing | İki külçe iki levha üretir; bir levha bir külçeye eritilir |
| 4 | Sertlik, patlama direnci, araç etiketleri, blok loot, 40 merdiven durumu | crystal-blocks | Blok düşer; tüm merdiven yönleri, yarımları ve köşe şekilleri görünür |
| 5 | Living entity, nitelikler, goal ve target listesi | forest-guardian | `/summon forest_guardian:guardian`; görüş içindeki oyuncuyu takip edip saldırır |
| 6 | Kaynak üretiminde balanced/hard profilleri | survival-basics | Hard kazma 120, balanced kazma 240 dayanıklılık; tarif verimi 1/3 |
| 7 | Sürümlü HMOD dosyaları, metadata, CI artifact ve yayın kontrol listesi | Altı örneğin sürümlü paketleri | Uyumlu APK'da kurulum, yeniden başlatma ve katalogdan güncelleme |

Kaynaklar hazırlanmıştır. Paket derleme ve gerçek HMOD parser kontrolü CI ile
doğrulanır. Oyun içi kontroller ve gerçek cihaz davranışı ayrıca tamamlanmalıdır;
paketin ayrıştırılması bunları kanıtlamaz. Metadata bu nedenle `catalog_enabled:
false` kullanır. Orman Bekçisi önceki Android AI geliştirme dalına ihtiyaç duyar.

## Yeni mod oluştur

```sh
python scripts/create_mod.py --template copper_tools --id my_tools --output work/my-tools
python scripts/create_mod.py --template survival_basics --id survival_hard --profile hard --output work/survival-hard
python scripts/build_hmod.py --source work/my-tools --output target/horizon-mod/my_tools-1.0.0.hmod
python scripts/build_examples.py
```

Oluşturucu mevcut dizinin üzerine yazmaz. Profil seçimi **paketleme öncesi** yapılır;
oyun içinde canlı ayar menüsü eklenmez. `balance-profile.json` kaynak üretim kaydıdır,
HMOD içine girmez. Değer değişince yeniden oluştur, sürümü artır ve paketi yeniden kur.

Araçlar vanilla demir/taş template'lerinin saldırı, zırh ve kazma davranışlarını
kullanır; özel saldırı formülü veya yalnız cevhere çalışan yeni olay kancası eklenmez.
Modeller vanilla kaynaklarına referans verir; bakır aletler şimdilik demir alet
görünümündedir. Kristal bloklar amethyst dokusuna referans verir. Orman Bekçisi
zombie modelini ve gündüz yanma davranışını korur; doğal spawn ve özel animasyon yoktur.

## Yayına geçiş

1. İlgili Android runtime değişikliklerini ana dala al ve hedef APK'yı üret.
2. Tablodaki oyun içi kontrolleri gerçek cihazda tamamla ve APK sürümünü kaydet.
3. Manifest sürümünü ve değişiklik notlarını güncelle; aynı sürümde farklı bayt yayımlama.
4. `mods/<id>/mod.json` içindeki `catalog_enabled` değerini ancak uyumluluk onaylanınca aç.
5. `id-version.hmod` dosyasını GitHub Release'e ekle. Yayın akışı boyut/SHA-256'yı üretir.
6. Katalogdan kurulum ve sürüm yükseltmeyi kontrol et.

CI artifacts bir GitHub Release değildir; bu tur otomatik olarak oyuncu kataloğuna yayın yapmaz.
