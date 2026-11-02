# Mod yayınlama ve katalog akışı

## Kaynak dosyalar

- **mods/<id>/mod.json**: mağazada gösterilecek mod bilgileri.
- **catalog/categories.json**: mağaza kategori kimlikleri ve görünen adları.
- **catalog/mods.json**: Actions tarafından üretilen istemci kataloğu.
- **GitHub Release**: sürümlenmiş .hmod indirme varlıkları.

## Yayınlama kuralları

- Yalnızca .hmod paketleri kabul edilir.
- Paket adı tam olarak <id>-<version>.hmod olmalıdır.
- Paket kökünde tam olarak bir horizon-mod.toml bulunmalıdır.
- ZIP içindeki mutlak yollar, üst dizine çıkan yollar ve ters eğik çizgi yolları reddedilir.
- Paket boyutu 1 byte ile 64 MiB arasında olmalıdır.
- Mod metadata kimliği paket manifestindeki ID ile aynı olmalıdır.
- Metadata içindeki kategori, catalog/categories.json içinde bulunmalıdır.
- İndirme adresleri bu deponun GitHub Releases alanına işaret eder.
- SHA-256 ve byte boyutu yayın sırasında yeniden hesaplanır.
- Önceki sürümler katalogda tutulur.
- Aynı mod sürümü farklı paket içeriğiyle tekrar yayımlanamaz.

## GitHub Actions

**Validate and publish mod catalog**
- Push ve pull request sırasında katalog, metadata ve örnek paketi doğrular.
- Bir Release yayımlandığında HMOD varlıklarını indirir, kataloğa ekler, tekrar doğrular ve katalog commit'ini main dalına gönderir.

**Build and publish example Ruby mod**
- Ruby örnek manifesti main dalında değiştiğinde paketi derler.
- Sürüm Release'i daha önce yayımlanmamışsa oluşturur.
- Katalog güncellemesini ayrı release-event workflow'suna bırakır.

## İstemci endpointleri

- https://raw.githubusercontent.com/Geko7490/MinecraftMod/main/catalog/mods.json
- https://raw.githubusercontent.com/Geko7490/MinecraftMod/main/catalog/categories.json

İstemci son başarılı ve doğrulanmış katalog kopyasını yerel depoda tutmalıdır. Ağ hatası veya geçersiz yeni katalog, mevcut önbelleğin üzerine yazmamalıdır.
