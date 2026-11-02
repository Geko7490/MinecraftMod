# Mod geliştirme rehberi

Bu rehber, Android sürümünde çalışan Horizon content modlarının hazırlanmasını ve MinecraftMod kataloğunda yayınlanmasını anlatır.

> Android istemcisi Fabric/Forge/NeoForge Java modlarını (`.jar`) çalıştırmaz. Katalog yalnızca Horizon'ın desteklediği `.hmod` paketlerini kabul eder. `.hnmod` native Rust paketleri Android'e yüklenemez.

## 1. Araçlar

Python 3.11+ ve Git yeterlidir. Content modları için Rust derleyicisi veya özel SDK kurulumu gerekmez.

## 2. Mod oluştur

Örnek projeyi kopyala ve mod kimliğini kendi moduna göre değiştir:

```bash
cp -R examples/ruby-content my-ruby
```

Content modları Rust kodu çalıştırmaz; desteklenen blok, eşya, tarif, loot table, model, texture ve dil verilerini paketler. Tam örnek: [examples/ruby-content](../examples/ruby-content/).

## 3. Yapı

```
ruby/
├── horizon-mod.toml
├── assets/ruby/{blockstates,items,models,textures,lang}/
└── data/ruby/{horizon/block,horizon/item,loot_table,recipe}/
```

## 4. Manifest

```toml
id = "ruby"
name = "Ruby"
version = "0.1.0"
description = "Adds a ruby gem and a ruby block"
authors = ["YourName"]
api = "0.2"
side = "both"
capabilities = ["registries"]
```

`id` küçük harf/rakam/alt çizgi, 1–64 karakter olmalı. `api = "0.2"` content API'sidir. `registries` blok/eşya kayıtlarını açar. Manifestte desteklenmeyen alanlar reddedilir.

## 5. Ruby içerik örneği

`data/ruby/horizon/block/ruby_block.json`:

```json
{"template":"minecraft:iron_block","properties":{"hardness":4.0,"light":3,"sounds":"minecraft:amethyst_block","map_color":28}}
```

`data/ruby/horizon/item/ruby.json`:

```json
{"template":"minecraft:diamond","rarity":"uncommon"}
```

İsimler `assets/ruby/lang/en_us.json` içinde:

```json
{"block.ruby.ruby_block":"Block of Ruby","item.ruby.ruby":"Ruby"}
```

Model, blockstate, texture, loot ve tarif dosyaları örnek projede bulunur. Desteklenen alanlar ve sınırlamalar: [Horizon mod dokümantasyonu](https://github.com/Geko7490/Minecraft/blob/android/docs/mods.md).

## 6. Derle ve kontrol et

```bash
python scripts/build_hmod.py --source my-ruby --output target/horizon-mod/ruby.hmod
```

Bu betik manifesti, capability değerlerini, dosya yollarını, JSON dosyalarını, PNG başlıklarını ve ZIP bütünlüğünü kontrol eder. Çıktı: `target/horizon-mod/ruby.hmod`. Oyun, kurulum sırasında manifesti, dosya boyutunu ve SHA-256 değerini yeniden doğrular. Android cihaz testi ayrıca gereklidir.

## 7. Katalog metadata

Katalog deposunda `mods/ruby/mod.json` oluştur:

```json
{
  "id": "ruby",
  "name": "Ruby",
  "description": "Adds a ruby gem and a ruby block.",
  "developer": "YourName",
  "type": "hmod",
  "license": "MIT",
  "source": "https://github.com/YourName/ruby-mod",
  "game_versions": ["26.3"]
}
```

`id` manifest ile aynı olmalı. `license` SPDX kimliğidir. `source` HTTPS kaynak kodu adresidir. Yalnızca test ettiğin oyun sürümlerini yaz.

## 8. Yayınla

Dosya adı `<id>-<version>.hmod` olmalı:

```bash
cp target/horizon-mod/ruby.hmod target/horizon-mod/ruby-0.1.0.hmod
gh release create v0.1.0 target/horizon-mod/ruby-0.1.0.hmod \
  --repo Geko7490/MinecraftMod --title "Ruby 0.1.0" --notes "Initial release."
```

Release **published** olunca Actions manifesti doğrular, API/side/capabilities bilgisini alır, dosya boyutu ve SHA-256 hesaplar ve `catalog/mods.json` dosyasını günceller. Başarısız doğrulama yayınlanmaz.

Yeni sürümde manifestteki `version` değerini artır, yeniden derle ve yeni GitHub Release yayımla. İlk örnek sürümünün manifesti `main` dalına alındığında GitHub Actions otomatik olarak paketi derler, Release oluşturur ve kataloğa ekler. Sonraki sürümlerde manifestteki sürüm numarasını artır.
