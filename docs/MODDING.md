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

## 5. Entity API

Entity tanımı `data/<id>/horizon/entity_type/<name>.json` altında bulunur.

### Projectile (geriye dönük uyumlu)

`kind` yazılmazsa `projectile` varsayılır. Şu an yalnızca `minecraft:snowball` şablonu desteklenir:

~~~json
{
  "template": "minecraft:snowball",
  "item": "my_mod:core",
  "damage": 4.0
}
~~~

Modun kendi item'ı projectile'ı fırlatır; bir item yalnızca tek entity türüne bağlanabilir.

### Living entity archetype

`kind: "living"` ile yeni bir entity ID'si oluşturulur ve desteklenen vanilla mob şablonlarından birinin davranışı, modeli, animasyonu ve sesleri yeniden kullanılır:

- `minecraft:zombie`
- `minecraft:skeleton`
- `minecraft:cow`
- `minecraft:pig`
- `minecraft:sheep`
- `minecraft:chicken`
- `minecraft:spider`
- `minecraft:creeper`
- `minecraft:wolf`
- `minecraft:iron_golem`

Örnek:

~~~json
{
  "kind": "living",
  "template": "minecraft:zombie",
  "attributes": {
    "minecraft:max_health": 40.0,
    "minecraft:movement_speed": 0.31,
    "minecraft:attack_damage": 7.0,
    "minecraft:follow_range": 32.0,
    "minecraft:armor": 4.0
  }
}
~~~

Desteklenen attribute alanları: `minecraft:max_health`, `minecraft:movement_speed`, `minecraft:attack_damage`, `minecraft:armor`, `minecraft:armor_toughness`, `minecraft:knockback_resistance`, `minecraft:follow_range`, `minecraft:jump_strength`, `minecraft:flying_speed`.

Living entity'ler henüz spawn egg kullanmaz; `/summon <mod_id>:<name>` ile çağrılır. İsim `entity.<mod_id>.<name>` dil anahtarıyla çevrilir. Örnek: [Vex Sentinel](../examples/vex-sentinel/).

**API sınırı:** Bu, vanilla archetype tabanlı yaşayan entity API'sidir; tamamen yeni AI API'si değildir. Modlar henüz kendi goal sınıflarını, hedef seçicilerini, pathfinding algoritmalarını, tick/event callback'lerini, model iskeletlerini veya animasyon controller'larını tanımlayamaz. Entity seçtiği vanilla template'in AI ve görsel davranışını kullanır.

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
