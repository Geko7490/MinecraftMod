#!/usr/bin/env python3
"""Create a complete content mod using supported HMOD 0.2 declarations.

Balance profiles are build-time settings. They do not install executable code
or claim to provide a runtime configuration API.
"""
import argparse
import json
from pathlib import Path
import re
import tempfile

TEMPLATES = {
    'copper_tools': 'Bakır Araçlar',
    'miner_kit': 'Madenci Seti',
    'copper_processing': 'Bakır İşleme',
    'crystal_blocks': 'Kristal Blokları',
    'forest_guardian': 'Orman Bekçisi',
    'survival_basics': 'Hayatta Kalma Temelleri',
}


def generate(template, mod_id, output, profile='balanced'):
    if template not in TEMPLATES or profile not in ('balanced', 'hard'):
        raise ValueError('Unknown template or balance profile')
    if not re.fullmatch(r'[a-z0-9_]{1,64}', mod_id):
        raise ValueError('Mod id must match [a-z0-9_]{1,64}')
    output = Path(output).absolute()
    if output.exists():
        raise ValueError('Output already exists; choose a new directory')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.hmod-', dir=output.parent) as temporary:
        root = Path(temporary) / 'source'
        root.mkdir()
        language = {}

        def write(path, value):
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

        def data(path, value):
            write(f'data/{mod_id}/{path}.json', value)

        def asset(path, value):
            write(f'assets/{mod_id}/{path}.json', value)

        def item(name, base, title, durability=None):
            declaration = {'template': f'minecraft:{base}'}
            if durability is not None:
                declaration.update(max_stack_size=1, components={
                    'minecraft:max_damage': max(1, durability // (2 if profile == 'hard' else 1))
                })
            data(f'horizon/item/{name}', declaration)
            asset(f'items/{name}', {'model': {'type': 'minecraft:model', 'model': f'minecraft:item/{base}'}})
            language[f'item.{mod_id}.{name}'] = title

        def shaped(name, pattern, keys, count=1):
            data(f'recipe/{name}', {'type': 'minecraft:crafting_shaped', 'category': 'misc',
                'pattern': pattern, 'key': keys, 'result': {'id': f'{mod_id}:{name}', 'count': count}})

        def block(name, base, title, stairs=False):
            data(f'horizon/block/{name}', {'template': f'minecraft:{base}', 'properties': {
                'hardness': 2.0, 'explosion_resistance': 6.0, 'requires_tool': True}})
            language[f'block.{mod_id}.{name}'] = title
            textures = {key: 'minecraft:block/amethyst_block' for key in ('bottom', 'top', 'side')}
            if stairs:
                for suffix, parent in [('', 'stairs'), ('_inner', 'inner_stairs'), ('_outer', 'outer_stairs')]:
                    asset(f'models/block/{name}{suffix}', {'parent': f'minecraft:block/{parent}', 'textures': textures})
                variants = {}
                for facing, rotation in [('east', 0), ('south', 90), ('west', 180), ('north', 270)]:
                    for half in ('bottom', 'top'):
                        for shape in ('straight', 'inner_left', 'inner_right', 'outer_left', 'outer_right'):
                            y = rotation + (-90 if shape.endswith('left') else 0)
                            if half == 'top' and shape != 'straight':
                                y += 90
                            suffix = '_inner' if shape.startswith('inner') else '_outer' if shape.startswith('outer') else ''
                            variants[f'facing={facing},half={half},shape={shape}'] = {
                                'model': f'{mod_id}:block/{name}{suffix}', 'x': 180 if half == 'top' else 0,
                                'y': y % 360, 'uvlock': True}
                asset(f'blockstates/{name}', {'variants': variants})
            else:
                asset(f'models/block/{name}', {'parent': 'minecraft:block/cube_all',
                    'textures': {'all': 'minecraft:block/amethyst_block'}})
                asset(f'blockstates/{name}', {'variants': {'': {'model': f'{mod_id}:block/{name}'}}})
            asset(f'items/{name}', {'model': {'type': 'minecraft:model', 'model': f'{mod_id}:block/{name}'}})
            data(f'loot_table/blocks/{name}', {'type': 'minecraft:block', 'pools': [{
                'rolls': 1, 'conditions': [{'condition': 'minecraft:survives_explosion'}],
                'entries': [{'type': 'minecraft:item', 'name': f'{mod_id}:{name}'}]}]})

        if template == 'copper_tools':
            for tool, pattern in [('sword', ['C', 'C', 'S']), ('pickaxe', ['CCC', ' S ', ' S ']), ('axe', ['CC', 'CS', ' S'])]:
                item(f'copper_{tool}', f'iron_{tool}', f'Bakır {tool}', 180)
                shaped(f'copper_{tool}', pattern, {'C': 'minecraft:copper_ingot', 'S': 'minecraft:stick'})
        elif template == 'miner_kit':
            item('mining_pickaxe', 'iron_pickaxe', 'Madenci Kazması', 512)
            item('mining_helmet', 'iron_helmet', 'Madenci Miğferi', 384)
            shaped('mining_pickaxe', ['III', ' S ', ' S '], {'I': 'minecraft:iron_ingot', 'S': 'minecraft:stick'})
            shaped('mining_helmet', ['III', 'I I'], {'I': 'minecraft:iron_ingot'})
        elif template == 'copper_processing':
            item('copper_plate', 'copper_ingot', 'Bakır Levha')
            shaped('copper_plate', ['CC'], {'C': 'minecraft:copper_ingot'}, 1 if profile == 'hard' else 2)
            data('recipe/recycle_plate', {'type': 'minecraft:smelting', 'category': 'misc',
                'ingredient': f'{mod_id}:copper_plate', 'result': {'id': 'minecraft:copper_ingot'},
                'experience': 0.1, 'cookingtime': 200})
        elif template == 'crystal_blocks':
            block('crystal_block', 'amethyst_block', 'Kristal Blok')
            block('crystal_stairs', 'quartz_stairs', 'Kristal Merdiven', stairs=True)
            shaped('crystal_block', ['AA', 'AA'], {'A': 'minecraft:amethyst_shard'})
            shaped('crystal_stairs', ['C  ', 'CC ', 'CCC'], {'C': f'{mod_id}:crystal_block'}, 2 if profile == 'hard' else 4)
            for tag in ('mineable/pickaxe', 'needs_stone_tool'):
                write(f'data/minecraft/tags/block/{tag}.json', {'replace': False,
                    'values': [f'{mod_id}:crystal_block', f'{mod_id}:crystal_stairs']})
        elif template == 'forest_guardian':
            data('horizon/entity_type/guardian', {'kind': 'living', 'template': 'minecraft:zombie',
                'attributes': {'minecraft:max_health': 60.0 if profile == 'hard' else 40.0,
                    'minecraft:attack_damage': 8.0 if profile == 'hard' else 5.0,
                    'minecraft:movement_speed': 0.25, 'minecraft:follow_range': 24.0},
                'ai': {'mode': 'replace', 'goals': [{'type': 'float', 'priority': 0},
                    {'type': 'melee_attack', 'priority': 2, 'speed': 1.0, 'interval': 20},
                    {'type': 'stroll', 'priority': 5, 'speed': 0.8},
                    {'type': 'look_at_player', 'priority': 6, 'range': 10.0}],
                    'targets': [{'type': 'hurt_by', 'priority': 1},
                        {'type': 'nearest_player', 'priority': 2, 'must_see': True, 'interval': 10}]}})
            language[f'entity.{mod_id}.guardian'] = 'Orman Bekçisi'
        else:
            item('field_pickaxe', 'stone_pickaxe', 'Arazi Kazması', 240)
            item('supply_token', 'paper', 'Erzak Fişi')
            shaped('field_pickaxe', ['CCC', ' S ', ' S '], {'C': 'minecraft:cobblestone', 'S': 'minecraft:stick'})
            shaped('supply_token', ['PPP'], {'P': 'minecraft:paper'}, 1 if profile == 'hard' else 3)

        item_ids = sorted(p.stem for p in (root / f'data/{mod_id}/horizon/item').glob('*.json'))
        item_ids += sorted(p.stem for p in (root / f'data/{mod_id}/horizon/block').glob('*.json'))
        if item_ids:
            data('horizon/creative_tab/examples', {'title': TEMPLATES[template],
                'icon': f'{mod_id}:{item_ids[0]}', 'items': [f'{mod_id}:{name}' for name in item_ids]})
        asset('lang/tr_tr', language)
        asset('lang/en_us', {key: key.rsplit('.', 1)[-1].replace('_', ' ').title() for key in language})
        (root / 'horizon-mod.toml').write_text(
            f'id = "{mod_id}"\nname = "{TEMPLATES[template]}"\nversion = "1.0.0"\n'
            f'description = "HMOD example: {template}; profile {profile}"\n'
            'authors = ["Geko7490"]\napi = "0.2"\nside = "both"\ncapabilities = ["registries"]\n', encoding='utf-8')
        write('balance-profile.json', {'template': template, 'profile': profile, 'configuration': 'build-time'})
        (root / 'README.md').write_text(
            f'# {TEMPLATES[template]}\n\nID: `{mod_id}`. Profile: `{profile}`. Version: 1.0.0.\n\n'
            'Requires Minecraft 26.3 / HMOD API 0.2. Assets reference vanilla models/textures; tools retain vanilla visuals and attack/mining behavior. Durability is overridden.\n\n'
            + (f'Requires the Android AI runtime branch. Spawn with `/summon {mod_id}:guardian`. This is a hostile zombie archetype, including daylight burning; no natural spawning or custom rig is added.\n\n' if template == 'forest_guardian' else '')
            + f'Build: `python scripts/build_hmod.py --source examples/{template.replace("_", "-")} --output target/horizon-mod/{mod_id}-1.0.0.hmod`\n\n'
            'Profiles are selected when creating the source, then require rebuilding and reinstalling. Increase the manifest version before publishing changed bytes. See docs/MOD_ROADMAP.md for in-game acceptance checks.\n', encoding='utf-8')
        root.rename(output)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', choices=sorted(TEMPLATES), required=True)
    parser.add_argument('--id', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--profile', choices=['balanced', 'hard'], default='balanced')
    args = parser.parse_args()
    try:
        generate(args.template, args.id, args.output, args.profile)
    except ValueError as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
