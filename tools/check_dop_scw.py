from __future__ import annotations

import math
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / 'common/decisions/DOP_SCW_decisions.txt'
GENERATOR = ROOT / 'tools/generate_dop_scw_decisions.py'
LOCALISATION = ROOT / 'localisation/simp_chinese/DOP_SCW_decisions_l_simp_chinese.yml'
BASE_LOCALISATION = ROOT / 'localisation/simp_chinese/DOP_SiliconCW_l_simp_chinese.yml'
EFFECTS = ROOT / 'common/scripted_effects/DOP_SCW_effects.txt'
GROWTH = ROOT / 'common/scripted_effects/DOP_SCW_growth_effects.txt'
ON_ACTIONS = ROOT / 'common/on_actions/DOP_SCW_on_actions.txt'
DEBUG = ROOT / 'common/decisions/DOP_debug_decision.txt'
BOP_DECISIONS = ROOT / 'common/decisions/DOP_bop_decision.txt'
GUI = ROOT / 'interface/GUI/DOP_silicon_CW_interface.gui'

GROUPS = ('race', 'materials', 'wafer', 'lithography', 'packaging', 'logistics')


def read(path: Path, encoding: str = 'utf-8-sig') -> str:
    return path.read_text(encoding=encoding)


def decision_blocks(text: str) -> dict[str, str]:
    blocks: dict[str, str] = {}
    pattern = re.compile(r'^    (DOP_SCW_[a-z0-9_]+) = \{', re.MULTILINE)
    for match in pattern.finditer(text):
        depth = 0
        quote = False
        escaped = False
        end = None
        for index in range(match.end() - 1, len(text)):
            char = text[index]
            if escaped:
                escaped = False
                continue
            if char == '\\' and quote:
                escaped = True
                continue
            if char == chr(34):
                quote = not quote
                continue
            if quote:
                continue
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    end = index + 1
                    break
        if end is None:
            raise AssertionError(f'unclosed decision block: {match.group(1)}')
        blocks[match.group(1)] = text[match.start():end]
    return blocks


def braces_balanced(path: Path) -> bool:
    text = read(path, 'utf-8-sig')
    depth = 0
    quote = False
    escaped = False
    comment = False
    for char in text:
        if comment:
            if char == '\n':
                comment = False
            continue
        if escaped:
            escaped = False
            continue
        if char == '\\' and quote:
            escaped = True
            continue
        if char == chr(34):
            quote = not quote
            continue
        if quote:
            continue
        if char == '#':
            comment = True
        elif char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth < 0:
                return False
    return depth == 0 and not quote


def main() -> int:
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    generated = subprocess.run(
        [sys.executable, str(GENERATOR), '--check'],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    print(generated.stdout, end='')
    if generated.stderr:
        print(generated.stderr, file=sys.stderr, end='')
    require(generated.returncode == 0, 'generated SCW files are out of date')

    decisions_text = read(DECISIONS, 'utf-8')
    blocks = decision_blocks(decisions_text)
    require(len(blocks) == 48, f'expected 48 decisions, found {len(blocks)}')
    repeatable = {key: value for key, value in blocks.items() if 'days_remove = 30' in value}
    annual = {key: value for key, value in blocks.items() if 'days_remove = 365' in value}
    require(len(repeatable) == 24, f'expected 24 repeatable decisions, found {len(repeatable)}')
    require(len(annual) == 24, f'expected 24 annual decisions, found {len(annual)}')

    for group_index, group in enumerate(GROUPS):
        prefix = f'DOP_SCW_{group}_'
        group_blocks = [(key, block) for key, block in blocks.items() if key.startswith(prefix)]
        require(len(group_blocks) == 8, f'{group}: expected 8 decisions, found {len(group_blocks)}')
        group_repeatable = [(key, block) for key, block in group_blocks if key in repeatable]
        group_annual = [(key, block) for key, block in group_blocks if key in annual]
        require(len(group_repeatable) == 4, f'{group}: expected 4 repeatable decisions')
        require(len(group_annual) == 4, f'{group}: expected 4 annual decisions')
        for key, block in group_blocks:
            expected_page = 1 if group_index == 0 else 2
            require(
                f'selected_decision_tabs_id = {expected_page}' in block,
                f'{key}: wrong SCW page binding',
            )
            if group_index:
                require(
                    f'chain_part_selected = {group_index}' in block,
                    f'{key}: wrong industry-chain button binding',
                )
        for position, (key, block) in enumerate(group_annual):
            if position:
                previous_key = group_annual[position - 1][0]
                previous_flag = f'has_country_flag = {previous_key}_complete'
                require(block.count(previous_flag) >= 2, f'{key}: previous annual stage is not enforced')

    for key, block in blocks.items():
        require(
            block.count('has_country_flag = DOP_SCW_decisions_unlocked') >= 2,
            f'{key}: common unlock flag missing from visible/available',
        )
        require('date > 1977.1.1' in block, f'{key}: 1977 gate missing')
        require('custom_cost_text =' in block, f'{key}: custom cost localisation missing')
        require('custom_cost_trigger = {' in block, f'{key}: custom cost trigger missing')
        require('complete_effect = {' in block, f'{key}: upfront cost effect missing')
        require('remove_effect = {' in block, f'{key}: completion reward effect missing')
        require('ai_will_do = { factor = 0 }' in block, f'{key}: AI guard missing')
        if key in repeatable:
            require('days_re_enable = 90' in block, f'{key}: 90-day cooldown missing')
            require('fire_only_once' not in block, f'{key}: repeatable marked one-time')
            require(
                'TNO_improve_' not in block,
                f'{key}: permanent social-development growth must not stack on a repeatable decision',
            )
        else:
            require('fire_only_once = yes' in block, f'{key}: annual decision is not one-time')
            require('days_re_enable' not in block, f'{key}: annual decision has a cooldown')
            require('TNO_improve_' in block, f'{key}: annual social-development component missing')
        if key.startswith('DOP_SCW_lithography_'):
            require(
                block.count('has_country_flag = DOP_SCW_CCD_research_complete') >= 2,
                f'{key}: CCD prerequisite missing',
            )

    require(decisions_text.count('days_remove = 30') == 24, '30-day duration count mismatch')
    require(decisions_text.count('days_re_enable = 90') == 24, '90-day cooldown count mismatch')
    require(decisions_text.count('days_remove = 365') == 24, '365-day duration count mismatch')
    require(decisions_text.count('fire_only_once = yes') == 24, 'one-time decision count mismatch')
    require(
        all('TNO_improve_' not in block for block in repeatable.values()),
        'repeatable decisions contain permanently stacking SocDev helpers',
    )
    require(
        all('TNO_improve_' in block for block in annual.values()),
        'one or more annual milestones lack a SocDev helper',
    )
    emitted_icons = set(re.findall(r'^        icon = (GFX_[A-Za-z0-9_]+)$', decisions_text, re.MULTILINE))
    safe_icons = {
        'GFX_decision_GNG_generic',
        'GFX_decision_generic_document',
        'GFX_decision_generic_industry',
        'GFX_decision_generic_mining',
        'GFX_decision_generic_prepare_civil_war',
        'GFX_decision_generic_propaganda',
        'GFX_decision_generic_research',
    }
    require(emitted_icons <= safe_icons, f'undefined or unsafe decision icons emitted: {sorted(emitted_icons - safe_icons)}')

    effects_text = read(EFFECTS)
    baselines = {
        'GNG': ('135', '0.90'),
        'USA': ('310', '1.15'),
        'ITA': ('85', '0.85'),
        'GER': ('210', '1.00'),
        'JAP': ('225', '1.08'),
    }
    for tag, (production, compatibility) in baselines.items():
        require(
            f'scw_{tag}_production_value_t = {production}' in effects_text,
            f'{tag}: starting production value drifted',
        )
        require(
            f'scw_{tag}_compatibility_value_t = {compatibility}' in effects_text,
            f'{tag}: starting competitiveness value drifted',
        )
    require('has_country_flag = DOP_SCW_initialized' in effects_text, 'SCW initialization is not idempotent')
    require('DOP_SCW_apply_player_market_gain = {' in effects_text, 'combined player market helper missing')

    gdp_growth_values = [
        float(item)
        for item in re.findall(r'gdp_growth_temp = ([0-9.]+)', decisions_text)
    ]
    require(bool(gdp_growth_values), 'GDP growth rewards missing')
    require(
        min(gdp_growth_values, default=0) >= 0.1,
        'GDP growth values appear to use fractions instead of TNO percentage-point units',
    )
    require(
        max(gdp_growth_values, default=99) <= 0.6,
        'GDP growth reward exceeds the intended SCW balance ceiling',
    )
    for helper in (
        'GNG_China_opinion_change = yes',
        'GNG_Japan_approval_change = yes',
        'GNG_Corruption_Change = yes',
    ):
        require(helper in decisions_text, f'exact TNO Guangdong helper missing: {helper}')
    require('TNO_improve_poverty_rate_' not in decisions_text, 'invalid poverty SocDev helper remains')

    growth_text = read(GROWTH)
    random_factors = [float(item) for item in re.findall(r'DOP_SCW_growth_factor = ([0-9.]+)', growth_text)]
    require(bool(random_factors), 'opponent random growth factors missing')
    require(max(random_factors, default=99) <= 1.10, 'opponent random factor exceeds 1.10')
    require(min(random_factors, default=0) >= 1.00, 'opponent random factor is below 1.00')
    rates = {
        'USA': (0.17, 0.18),
        'ITA': (0.15, 0.16),
        'GER': (0.16, 0.17),
        'JAP': (0.19, 0.19),
    }
    for tag, (production_rate, competition_rate) in rates.items():
        require(
            f'scw_{tag}_production_value' in growth_text,
            f'{tag}: yearly production growth missing',
        )
        require(
            f'scw_{tag}_compatibility_value' in growth_text,
            f'{tag}: yearly competitiveness growth missing',
        )
        two_year_factor = math.pow(
            (1 + production_rate * 1.05) * (1 + competition_rate * 1.05),
            2,
        )
        require(
            1.80 <= two_year_factor <= 2.10,
            f'{tag}: composite two-year growth {two_year_factor:.3f} misses Moore-law band',
        )

    on_actions_text = read(ON_ACTIONS)
    for snippet in (
        'on_yearly = {',
        'original_tag = GNG',
        'has_country_flag = DOP_SCW_decisions_unlocked',
        'date > 1977.1.1',
        'DOP_SCW_apply_opponent_yearly_growth = yes',
    ):
        require(snippet in on_actions_text, f'yearly growth wiring missing: {snippet}')

    debug_text = read(DEBUG)
    debug_match = re.search(
        r'GNG_dop_debug_unlock_SCW_decisions = \{(?P<body>.*?)\n\s*GNG_dop_debug_remove_faction = \{',
        debug_text,
        re.DOTALL,
    )
    require(debug_match is not None, 'single SCW unlock debug decision missing')
    debug_body = debug_match.group('body') if debug_match else ''
    for snippet in (
        'set_country_flag = DOP_SCW_decisions_unlocked',
        'set_country_flag = DOP_SCW_CCD_research_complete',
        'GNG_SCW_Initialize = yes',
        'decision_tabs_id = 1',
        'decision_tabs_id = 2',
    ):
        require(snippet in debug_body, f'debug unlock wiring missing: {snippet}')
    require(
        re.search(
            r'GNG_dop_debug_enable_BOP_page_2 = \{.*?GNG_SCW_Initialize = yes',
            debug_text,
            re.DOTALL,
        ) is not None,
        'standalone SCW page-2 debug decision does not initialize data',
    )
    require('GNG_dop_show_chain_selected' not in read(BOP_DECISIONS), 'obsolete placeholder decision remains')

    gui_text = read(GUI)
    for button in range(2, 6):
        name = f'chain_btn_{button}_on'
        require(
            re.search(r'iconType = \{[^{}]*name = ' + chr(34) + name + chr(34), gui_text, re.DOTALL) is not None,
            f'{name}: selected-state overlay is still clickable',
        )

    loc_bytes = LOCALISATION.read_bytes()
    require(loc_bytes.startswith(b'\xef\xbb\xbf'), 'generated Simplified Chinese localisation lacks UTF-8 BOM')
    localisation_text = read(LOCALISATION)
    loc_keys = re.findall(r'^ ([A-Za-z0-9_]+):0 ', localisation_text, re.MULTILINE)
    require(len(loc_keys) == len(set(loc_keys)), 'generated localisation contains duplicate keys')
    for key in blocks:
        for suffix in ('', '_desc', '_cost', '_cost_blocked'):
            require(f' {key}{suffix}:0 ' in localisation_text, f'localisation missing: {key}{suffix}')
    base_loc = read(BASE_LOCALISATION)
    require('SCW_chain_part_5: "物流与管理"' in base_loc, 'fifth chain label was not corrected')
    require('CCD技术研发后解锁' in base_loc, 'lithography CCD prerequisite is not explained')

    banned = ('8英寸', '全自动晶圆传送', '原材料与销售', '海关免检绿色通道', '谈判统一ISO')
    combined_text = decisions_text + localisation_text + base_loc
    for phrase in banned:
        require(phrase not in combined_text, f'anachronistic or stale text remains: {phrase}')

    script_paths = (
        DECISIONS,
        EFFECTS,
        GROWTH,
        ON_ACTIONS,
        DEBUG,
        BOP_DECISIONS,
        GUI,
    )
    for path in script_paths:
        require(braces_balanced(path), f'unbalanced braces/quotes: {path.relative_to(ROOT)}')

    if errors:
        print('\nSCW static audit failed:', file=sys.stderr)
        for error in errors:
            print(f'  - {error}', file=sys.stderr)
        return 1
    print('SCW static audit passed: 48 decisions, six bindings, costs/rewards, growth, unlocks, and localisation.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
