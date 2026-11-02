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

Content modları Rust kodu çalıştırmaz; desteklenen blok, eşya, mob effect, entity type, menü, tarif, loot table, model, texture ve dil verilerini paketler. Örnekler: [Ruby content](../examples/ruby-content/) ve [Vex Spark entity](../examples/vex-spark/).

## 3. Paket yapısı

~~~text
my-mod/
├── horizon-mod.toml
├── assets/<namespace>/{blockstates,items,models,textures,lang}/
└── data/<namespace>/{horizon/block,horizon/item,horizon/mob_effect,horizon/entity_type,horizon/menu,loot_table,recipe}/
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

ID küçük harf/rakam/alt çizgi, 1–64 karakter olmalı. api = "0.2" content API'sidir. `registries` blok, eşya, mob effect, entity type ve menü kayıtlarını açar.

## 5. Entity type (fırlatılabilir entity)

Horizon'ın mevcut content EntityType API'si özel bir entity türünü, desteklenen bir vanilla projectile şablonundan kaydeder. Şu an desteklenen tek şablon `minecraft:snowball`'dır. Entity tanımı `data/<id>/horizon/entity_type/<name>.json` altında bulunur:

~~~json
{
  "template": "minecraft:snowball",
  "item": "my_mod:core",
  "damage": 4.0
}
~~~

- `template`: şu an yalnızca `minecraft:snowball`.
- `item`: aynı modun `data/<id>/horizon/item/` altında kaydettiği bir eşya. Bir eşya yalnızca tek entity türüne bağlanabilir.
- `damage`: çarpışmada hedefe verilecek thrown hasarı; varsayılan 0, negatif veya sonlu olmayan değerler reddedilir.
- Entity adı `entity.<mod_id>.<name>` çeviri anahtarıyla `assets/<id>/lang/en_us.json` içinde tanımlanır.
- Entity, bağlı eşyanın item modelini kullanır; eşya kullanıldığında snowball gibi fırlatılır. `/summon <mod_id>:<name>` ile de çağrılabilir.

**Sınırlar:** Bu bir yaşayan mob API'si değildir. Özel AI, hedef seçme, pathfinding, animasyon controller, model iskeleti, özel tick/event callback, dispenser davranışı veya özel entity sınıfı sağlamaz. Bunlar için native/engine tarafında yeni hook'lar gerekir. Detay ve çalışan paket örneği: [Vex Spark](../examples/vex-spark/).

## 6. Katalog metadata

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
  "icon": null,
  "screenshots": [],
  "license": "MIT",
  "source": "https://github.com/YourName/my-mod"
}
~~~

Zorunlu alanlar: id, name, description, developer, type, license, source. category, featured, tags, icon ve screenshots isteğe bağlıdır. Kategori kimlikleri [catalog/categories.json](../catalog/categories.json) içinde tanımlanır. Görsel adresleri HTTPS olmalıdır. Oyun sürümü ve API bilgisi yayınlanan HMOD manifestinden alınır; yalnızca gerçekten test ettiğin oyun sürümlerini yayın metadata'sında belirt.

## 7. Derle ve kontrol et

~~~bash
python scripts/build_hmod.py --source my-mod --output target/horizon-mod/my_mod.hmod
python scripts/validate_catalog.py
~~~

Derleyici manifesti, capability değerlerini, dosya yollarını, JSON dosyalarını, PNG başlıklarını, ZIP bütünlüğünü ve 64 MiB sınırını kontrol eder. EntityType şema ve oyun kayıt doğrulaması ayrıca Horizon'ın mod yükleyicisi tarafından yapılır.

## 8. Yayınla

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
