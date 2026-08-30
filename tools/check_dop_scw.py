from __future__ import annotations

import math
import re
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

from generate_dop_scw_decisions import DECISIONS as DECISION_DATA


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
UNLOCK_EFFECTS = ROOT / 'common/scripted_effects/DOP_SCW_unlock_effects.txt'
TEXTICON_GFX = ROOT / 'interface/GUI/DOP_SCW_texticons.gfx'
TEXTICON_DIR = ROOT / 'gfx/texticons/scw'
TEXTICON_BUILDER = ROOT / 'tools/build_dop_scw_texticons.py'

GROUPS = ('race', 'materials', 'wafer', 'lithography', 'packaging', 'logistics')


def read(path: Path, encoding: str = 'utf-8-sig') -> str:
    return path.read_text(encoding=encoding)


def numeric_text(raw: str | Decimal) -> str:
    """Render an exact Decimal without importing generator formatting logic."""
    rendered = format(Decimal(raw), 'f')
    if '.' in rendered:
        rendered = rendered.rstrip('0').rstrip('.')
    return rendered or '0'


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


def texticon_dds_ok(path: Path) -> bool:
    """Check the small BC3/ARGB texticon header used by the mod's DDS assets."""
    if not path.exists() or path.stat().st_size < 128:
        return False
    header = path.read_bytes()[:128]
    if header[:4] != b'DDS ':
        return False
    # DDS_HEADER fields: size, flags, height, width, pitch, depth, mipmapcount.
    size, flags, height, width, _pitch, depth, mipmaps = __import__('struct').unpack_from('<7I', header, 4)
    return (
        size == 124 and width == 18 and height == 18 and depth == 1 and
        mipmaps == 1 and flags == 0x2100F
    )


def visible_complete_calls(block: str, names: tuple[str, ...]) -> set[str]:
    """Return wrapper calls directly in complete_effect, outside hidden_effect."""
    lines = block.splitlines()
    in_complete = False
    complete_depth = 0
    hidden_depth: int | None = None
    found: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if not in_complete:
            if stripped.startswith('complete_effect = {'):
                in_complete = True
                complete_depth = 1
            continue
        # The generated format keeps direct effect calls at 12 spaces and
        # hidden calls at 16 spaces.  This also avoids mistaking a nested
        # hidden helper for an effect shown in the selection preview.
        if stripped.startswith('hidden_effect = {'):
            hidden_depth = complete_depth
        if hidden_depth is None and line.startswith('            '):
            for name in names:
                if re.search(rf'\b{re.escape(name)}\s*=\s*yes\b', stripped):
                    found.add(name)
        # Count braces conservatively; generated SCW blocks contain no quoted
        # braces in this section.
        complete_depth += line.count('{') - line.count('}')
        if hidden_depth is not None and complete_depth <= hidden_depth:
            hidden_depth = None
        if complete_depth <= 0:
            break
    return found


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
    decision_data = {decision.key: decision for decision in DECISION_DATA}
    require(len(blocks) == 48, f'expected 48 decisions, found {len(blocks)}')
    require(set(blocks) == set(decision_data), 'generated decision keys differ from generator source data')
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
        for (key, block), (next_key, _next_block) in zip(group_annual, group_annual[1:]):
            require(
                f'{next_key}_unlock = yes' in block,
                f'{key}: completion does not unlock next annual stage {next_key}',
            )

    for key, block in blocks.items():
        require(
            block.count('has_country_flag = DOP_SCW_decisions_unlocked') >= 2,
            f'{key}: common unlock flag missing from visible/available',
        )
        own_unlock = f'has_country_flag = {key}_unlocked'
        require(block.count(own_unlock) >= 2, f'{key}: individual unlock flag missing from visible/available')
        require(
            block.count('check_variable = { TNO_BoP_SelectedTab = token:BoP_Tab_DOPSiliconCW }') == 1,
            f'{key}: SCW BoP-tab visibility gate missing or duplicated',
        )
        require(not re.search(r'阶段[一二三四]：', block), f'{key}: stage prefix remains in decision title')
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

    # Monetary costs are deliberately fungible in TNO: reserves are spent
    # first and any deficit becomes debt.  They must not be gated by the
    # reserve variable or expose the implementation detail in localisation.
    require('money_reserves >' not in decisions_text, 'money/reserves cost still uses a money_reserves trigger')
    require(
        decisions_text.count('econ_spend_money_once_effect_raw_money = yes') >= 1,
        'no unified TNO money-spending effect found',
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
    require('DOP_SCW_apply_player_market_gain = yes' not in decisions_text, 'decisions still use obsolete combined market helper')
    for helper in ('DOP_SCW_change_audience_patience', 'DOP_SCW_change_supervisor_attitude', 'DOP_SCW_change_stage_integrity'):
        require(f'{helper} = {{' in effects_text, f'{helper}: visible SCW wrapper missing')
    wrapper_names = (
        'DOP_SCW_change_audience_patience',
        'DOP_SCW_change_supervisor_attitude',
        'DOP_SCW_change_stage_integrity',
    )
    cost_variables = {
        'DOP_SCW_change_audience_patience': 'DOP_SCW_audience_patience_change',
        'DOP_SCW_change_supervisor_attitude': 'DOP_SCW_supervisor_attitude_change',
        'DOP_SCW_change_stage_integrity': 'DOP_SCW_stage_integrity_change',
    }
    for key, block in blocks.items():
        visible_calls = visible_complete_calls(block, wrapper_names)
        for wrapper, variable in cost_variables.items():
            if re.search(rf'{variable}\s*=\s*-', block):
                require(wrapper in visible_calls, f'{key}: {wrapper} cost is hidden from selection preview')
    require('SCW_production_scale_increase = yes' in decisions_text, 'direct SCW production template call missing')
    require('SCW_compatibility_increase = yes' in decisions_text, 'direct SCW competitiveness template call missing')

    theater_effects = {
        'stage': ('DOP_SCW_stage_integrity_change', 'GFX_DOP_SCW_stage_integrity_texticon', ''),
        'supervisor': ('DOP_SCW_supervisor_attitude_change', 'GFX_DOP_SCW_supervisor_attitude_texticon', '%'),
        'audience': ('DOP_SCW_audience_patience_change', 'GFX_DOP_SCW_audience_patience_texticon', '%'),
    }
    combined_keys: set[str] = set()
    for key, decision in decision_data.items():
        block = blocks.get(key, '')
        for kind, (variable, _icon, _suffix) in theater_effects.items():
            if raw_cost := decision.costs.get(kind):
                expected = numeric_text(Decimal(raw_cost) * 2)
                require(
                    f'set_temp_variable = {{ {variable} = -{expected} }}' in block,
                    f'{key}: {kind} cost is not exactly doubled to {expected}',
                )
            if raw_reward := decision.rewards.get(kind):
                expected = numeric_text(Decimal(raw_reward) * 2)
                require(
                    f'set_temp_variable = {{ {variable} = {expected} }}' in block,
                    f'{key}: {kind} reward is not exactly doubled to {expected}',
                )

        scale = decision.rewards.get('scale')
        competition = decision.rewards.get('competition')
        if scale and competition and Decimal(scale) and Decimal(competition):
            combined_keys.add(key)
            require(
                f'set_temp_variable = {{ DOP_SCW_production_scale_change = {numeric_text(scale)} }}' in block,
                f'{key}: combined production value is missing',
            )
            require(
                f'set_temp_variable = {{ DOP_SCW_competition_change = {numeric_text(competition)} }}' in block,
                f'{key}: combined competitiveness value is missing',
            )
            require(
                block.count('DOP_SCW_change_production_and_competition = yes') == 1,
                f'{key}: dedicated combined market tooltip wrapper missing or duplicated',
            )
            require('SCW_production_scale_increase = yes' not in block, f'{key}: production still emits a separate tooltip')
            require('SCW_compatibility_increase = yes' not in block, f'{key}: competitiveness still emits a separate tooltip')
        else:
            require(
                'DOP_SCW_change_production_and_competition = yes' not in block,
                f'{key}: combined market wrapper used without both values',
            )
    require(bool(combined_keys), 'no decisions exercise the combined production/competitiveness tooltip')
    require(
        'DOP_SCW_change_production_and_competition = {' in effects_text,
        'dedicated production/competitiveness wrapper definition missing',
    )
    require(
        'custom_effect_tooltip = DOP_SCW_production_and_competition_increase_tt' in effects_text,
        'combined production/competitiveness tooltip is not exposed',
    )
    combined_wrapper_match = re.search(
        r'DOP_SCW_change_production_and_competition\s*=\s*\{(?P<body>.*?)\n\}',
        effects_text,
        re.DOTALL,
    )
    combined_wrapper = combined_wrapper_match.group('body') if combined_wrapper_match else ''
    require('hidden_effect = {' in combined_wrapper, 'combined market implementation is not hidden')
    require('set_temp_variable = { change_t = DOP_SCW_production_scale_change }' in combined_wrapper, 'combined production value is not copied into change_t')
    require('set_temp_variable = { change_t = DOP_SCW_competition_change }' in combined_wrapper, 'combined competitiveness value is not copied into change_t')
    require('SCW_production_scale_increase = yes' in combined_wrapper, 'combined wrapper does not apply production')
    require('SCW_compatibility_increase = yes' in combined_wrapper, 'combined wrapper does not apply competitiveness')

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
        require(helper in effects_text, f'exact TNO Guangdong helper missing from SCW wrappers: {helper}')
    require('TNO_improve_poverty_rate_' not in decisions_text, 'invalid poverty SocDev helper remains')

    unlock_text = read(UNLOCK_EFFECTS) if UNLOCK_EFFECTS.exists() else ''
    require(UNLOCK_EFFECTS.exists(), 'individual SCW unlock scripted-effects file is missing')
    unlock_effects = re.findall(r'^\s*(DOP_SCW_[a-z0-9_]+_unlock)\s*=\s*\{', unlock_text, re.MULTILINE)
    require(len(unlock_effects) == 48, f'expected 48 individual unlock effects, found {len(unlock_effects)}')
    for key in blocks:
        flag = f'{key}_unlocked'
        require(f'set_country_flag = {flag}' in unlock_text, f'{key}: unlock effect does not set its own flag')
        require(f'custom_effect_tooltip = {key}_unlock_tt' in unlock_text, f'{key}: unlock effect tooltip missing')
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
    debug_unlock_count = len(re.findall(r'set_country_flag = DOP_SCW_[a-z0-9_]+_unlocked', debug_body))
    require(
        debug_unlock_count == 48 or 'DOP_SCW_debug_unlock_all_decisions = yes' in debug_body,
        'debug unlock does not cover all 48 individual decision flags',
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
    loc_lines = {
        match.group('key'): match.group(0)
        for match in re.finditer(
            r'^ (?P<key>[A-Za-z0-9_]+):0 .*$',
            localisation_text,
            re.MULTILINE,
        )
    }
    for key in blocks:
        for suffix in ('', '_desc', '_cost', '_cost_blocked'):
            require(f' {key}{suffix}:0 ' in localisation_text, f'localisation missing: {key}{suffix}')
        unlock_key = f'{key}_unlock_tt'
        require(f' {unlock_key}:0 ' in localisation_text, f'localisation missing: {unlock_key}')
        unlock_line = next((line for line in localisation_text.splitlines() if line.startswith(f' {unlock_key}:0 ')), '')
        for fragment in ('£GFX_green_dollar_sign', '£GFX_decision_icon_small', '三微米冷战', '已经', '§G可用§!'):
            require(fragment in unlock_line, f'{unlock_key}: missing unlock formatting fragment {fragment}')
        flag_line = loc_lines.get(f'{key}_unlocked', '')
        for fragment in ('£GFX_decision_icon_small', f'${key}$', '§Y', '§G解锁§!'):
            require(fragment in flag_line, f'{key}_unlocked: missing coloured flag fragment {fragment}')
        if key in annual:
            complete_line = loc_lines.get(f'{key}_complete', '')
            for fragment in ('£GFX_decision_icon_small', f'${key}$', '§Y', '§G完成§!'):
                require(fragment in complete_line, f'{key}_complete: missing coloured flag fragment {fragment}')

        decision = decision_data.get(key)
        if decision:
            cost_line = loc_lines.get(f'{key}_cost', '')
            blocked_line = loc_lines.get(f'{key}_cost_blocked', '')
            for kind, (_variable, icon, suffix) in theater_effects.items():
                raw_cost = decision.costs.get(kind)
                if not raw_cost:
                    continue
                expected = numeric_text(Decimal(raw_cost) * 2)
                require(
                    f'£{icon} §Y{expected}{suffix}§!' in cost_line,
                    f'{key}: {kind} cost icon/number is not doubled or correctly coloured',
                )
                require(
                    f'£{icon} §R{expected}{suffix}§!' in blocked_line,
                    f'{key}: blocked {kind} cost icon/number is not doubled or correctly coloured',
                )
            for label in ('舞台完整度', '监制的态度', '观众的耐心'):
                require(label not in cost_line, f'{key}: theatre label remains in normal cost text: {label}')
                require(label not in blocked_line, f'{key}: theatre label remains in blocked cost text: {label}')

    combined_loc = loc_lines.get('DOP_SCW_production_and_competition_increase_tt', '')
    for fragment in (
        '§C产业规模§!',
        '[?DOP_SCW_production_scale_change]',
        '§m竞争力§!',
        '[?DOP_SCW_competition_change|2%]',
        '§G提升§!',
    ):
        require(fragment in combined_loc, f'combined market tooltip missing fragment: {fragment}')
    global_flag_colours = {
        'DOP_SCW_decisions_unlocked': '§G解锁§!',
        'DOP_SCW_CCD_research_complete': '§G完成§!',
        'DOP_SCW_enabled': '§G启用§!',
        'DOP_SCW_off': '§R关闭§!',
        'DOP_SCW_initialized': '§G初始化§!',
    }
    for flag, coloured_state in global_flag_colours.items():
        flag_line = loc_lines.get(flag, '')
        require(bool(flag_line), f'flag localisation missing: {flag}')
        require(coloured_state in flag_line, f'{flag}: state text is not coloured as expected')
    flag_source_text = '\n'.join((
        decisions_text,
        effects_text,
        unlock_text,
        growth_text,
        on_actions_text,
        debug_text,
        gui_text,
    ))
    referenced_scw_flags = set(re.findall(
        r'(?:has_country_flag|set_country_flag|clr_country_flag)\s*=\s*(DOP_SCW_[A-Za-z0-9_]+)',
        flag_source_text,
    ))
    missing_flag_localisations = sorted(referenced_scw_flags - set(loc_lines))
    require(
        not missing_flag_localisations,
        f'SCW country flags lack localisation: {missing_flag_localisations}',
    )
    for phrase in ('流动准备金', '一次性支出'):
        require(phrase not in localisation_text, f'cost localisation still exposes implementation detail: {phrase}')
    base_loc = read(BASE_LOCALISATION)
    require('SCW_chain_part_5: "物流与管理"' in base_loc, 'fifth chain label was not corrected')
    require('CCD技术研发后解锁' in base_loc, 'lithography CCD prerequisite is not explained')

    banned = ('8英寸', '全自动晶圆传送', '原材料与销售', '海关免检绿色通道', '谈判统一ISO')
    combined_text = decisions_text + localisation_text + base_loc
    for phrase in banned:
        require(phrase not in combined_text, f'anachronistic or stale text remains: {phrase}')

    require(TEXTICON_GFX.exists(), 'SCW texticon GFX registration is missing')
    gfx_text = read(TEXTICON_GFX)
    require(TEXTICON_BUILDER.exists(), 'SCW texticon builder is missing')
    builder_text = read(TEXTICON_BUILDER)
    for fragment in (
        'flag_root / "CHI.tga"',
        'flag_root / "JAP.tga"',
        'overlay_hourglass',
        'overlay_approval_check',
        'corruption_yen_icon()',
    ):
        require(fragment in builder_text, f'texticon builder lost required identity source: {fragment}')
    texticon_payloads: list[bytes] = []
    for stem in ('audience_patience', 'supervisor_attitude', 'stage_integrity'):
        sprite = f'GFX_DOP_SCW_{stem}_texticon'
        require(sprite in gfx_text, f'{sprite}: GFX registration missing')
        asset = TEXTICON_DIR / f'{stem}_texticon.dds'
        require(texticon_dds_ok(asset), f'{asset.relative_to(ROOT)}: invalid 18x18 DDS header')
        texticon_payloads.append(asset.read_bytes()[128:])
        png = TEXTICON_DIR / f'{stem}_texticon.png'
        require(png.exists(), f'{png.relative_to(ROOT)}: source PNG missing')
    require(len(set(texticon_payloads)) == 3, 'SCW texticons are not visually distinct at the pixel level')

    script_paths = (
        DECISIONS,
        EFFECTS,
        GROWTH,
        ON_ACTIONS,
        DEBUG,
        BOP_DECISIONS,
        GUI,
        UNLOCK_EFFECTS,
        TEXTICON_GFX,
    )
    for path in script_paths:
        require(braces_balanced(path), f'unbalanced braces/quotes: {path.relative_to(ROOT)}')

    if errors:
        print('\nSCW static audit failed:', file=sys.stderr)
        for error in errors:
            print(f'  - {error}', file=sys.stderr)
        return 1
    print('SCW static audit passed: 48 decisions, SCW-tab visibility, doubled theatre values, combined market tooltips, flags, and localisation.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
