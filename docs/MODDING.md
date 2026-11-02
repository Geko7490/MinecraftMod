# Mod geliştirme rehberi

Bu rehber, Android sürümünde çalışan Horizon content modlarının hazırlanmasını ve MinecraftMod kataloğunda yayınlanmasını anlatır.

> Android istemcisi Fabric/Forge/NeoForge Java modlarını (.jar) çalıştırmaz. Katalog yalnızca Horizon'ın desteklediği .hmod paketlerini kabul eder. Native .hnmod paketleri bu mağazanın kapsamı dışındadır.

## 1. Araçlar

Python 3.11+ ve Git yeterlidir. Content modları için Rust derleyicisi veya özel SDK kurulumu gerekmez.

## 2. Mod oluştur

Örnek projeyi kopyala ve mod kimliğini kendi moduna göre değiştir:

~~~bash
cp -R examples/ruby-content my-mod
~~~

Content modları Rust kodu çalıştırmaz; desteklenen blok, eşya, tarif, loot table, model, texture ve dil verilerini paketler. Tam örnek: [examples/ruby-content](../examples/ruby-content/).

## 3. Paket yapısı

~~~text
my-mod/
├── horizon-mod.toml
├── assets/<namespace>/{blockstates,items,models,textures,lang}/
└── data/<namespace>/{horizon/block,horizon/item,loot_table,recipe}/
~~~

## 4. Paket manifesti

~~~toml
id = "my_mod"
name = "My Mod"
version = "1.0.0"
description = "A short description"
authors = ["YourName"]
api = "0.2"
side = "both"
capabilities = ["registries"]
~~~

ID küçük harf/rakam/alt çizgi, 1–64 karakter olmalı. api = "0.2" content API'sidir. registries blok/eşya kayıtlarını açar.

## 5. Katalog metadata

Katalog deposunda **mods/<id>/mod.json** oluştur:

~~~json
{
  "id": "my_mod",
  "name": "My Mod",
  "description": "A short description.",
  "developer": "YourName",
  "type": "hmod",
  "category": "items",
  "featured": false,
  "tags": ["items", "utility"],
  "icon": "https://raw.githubusercontent.com/Geko7490/MinecraftMod/main/assets/mods/my_mod/icon.png",
  "screenshots": [],
  "license": "MIT",
  "source": "https://github.com/YourName/my-mod",
  "game_versions": ["26.3"]
}
~~~

Zorunlu alanlar: id, name, description, developer, type, license, source, game_versions. category, featured, tags, icon ve screenshots isteğe bağlıdır. Kategori kimlikleri [catalog/categories.json](../catalog/categories.json) içinde tanımlanır. Görsel adresleri HTTPS olmalıdır. Yalnızca gerçekten test ettiğin oyun sürümlerini yaz.

## 6. Derle ve kontrol et

~~~bash
python scripts/build_hmod.py --source my-mod --output target/horizon-mod/my_mod.hmod
python scripts/validate_catalog.py
~~~

Derleyici manifesti, capability değerlerini, dosya yollarını, JSON dosyalarını, PNG başlıklarını, ZIP bütünlüğünü ve 64 MiB sınırını kontrol eder.

## 7. Yayınla

Dosya adı **<id>-<version>.hmod** olmalı:

~~~bash
cp target/horizon-mod/my_mod.hmod target/horizon-mod/my_mod-1.0.0.hmod
gh release create v1.0.0 target/horizon-mod/my_mod-1.0.0.hmod \
  --repo Geko7490/MinecraftMod --title "My Mod 1.0.0" --notes "Initial release."
~~~

Release yayımlandığında GitHub Actions:
1. Release içindeki HMOD paketlerini indirir.
2. ZIP içeriğini ve kök manifestini doğrular.
3. Mod ID, sürüm, API ve metadata eşleşmesini kontrol eder.
4. SHA-256 ve tam dosya boyutunu hesaplar.
5. Yeni sürümü kataloğa ekler; eski sürümleri korur.
6. Kataloğu doğrular ve catalog/mods.json dosyasını günceller.

Yayımlanmış bir mod sürümünün paket baytları değiştirilemez. Aynı sürüm farklı SHA-256 ile yeniden yayımlanmaya çalışılırsa yayın doğrulaması başarısız olur. Yeni paket için sürüm numarasını artır.

Ayrıntılar: [Publishing guide](PUBLISHING.md).
