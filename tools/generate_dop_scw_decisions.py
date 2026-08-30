from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISIONS_PATH = ROOT / 'common/decisions/DOP_SCW_decisions.txt'
LOCALISATION_PATH = ROOT / 'localisation/simp_chinese/DOP_SCW_decisions_l_simp_chinese.yml'
UNLOCK_EFFECTS_PATH = ROOT / 'common/scripted_effects/DOP_SCW_unlock_effects.txt'

GROUP_KEYS = ('race', 'materials', 'wafer', 'lithography', 'packaging', 'logistics')
SAFE_DECISION_ICONS = {
    'GFX_decision_GNG_generic',
    'GFX_decision_generic_document',
    'GFX_decision_generic_industry',
    'GFX_decision_generic_mining',
    'GFX_decision_generic_prepare_civil_war',
    'GFX_decision_generic_propaganda',
    'GFX_decision_generic_research',
}


@dataclass(frozen=True)
class Decision:
    group: int
    slug: str
    title: str
    desc: str
    costs: dict[str, str]
    rewards: dict[str, str]
    socdev: tuple[str, ...] = ()
    stage: int = 0
    icon: str = 'GFX_decision_GNG_generic'

    @property
    def key(self) -> str:
        return f'DOP_SCW_{GROUP_KEYS[self.group]}_{self.slug}'

    @property
    def unlock_flag(self) -> str:
        return f'{self.key}_unlocked'

    @property
    def unlock_effect(self) -> str:
        return f'{self.key}_unlock'

    @property
    def unlock_tooltip(self) -> str:
        return f'{self.key}_unlock_tt'

    @property
    def repeatable(self) -> bool:
        return self.stage == 0

    @property
    def applied_socdev(self) -> tuple[str, ...]:
        # TNO SocDev helpers permanently raise monthly development progress.
        # Restrict them to one-time annual milestones so 90-day activities
        # cannot stack an unbounded permanent modifier.
        return self.socdev if not self.repeatable else ()


def E(
    group: int,
    slug: str,
    title: str,
    desc: str,
    costs: dict[str, str],
    rewards: dict[str, str],
    socdev: tuple[str, ...] = (),
    stage: int = 0,
    icon: str = 'GFX_decision_GNG_generic',
) -> Decision:
    return Decision(group, slug, title, desc, costs, rewards, socdev, stage, icon)


DECISIONS: list[Decision] = []

DECISIONS.extend([
    E(0, 'commercial_attaches', '派遣科技武官开展商业技术情报收集',
      '驻外武官的公文包向来比军服更有用。只要经费按时汇入，散落在实验室酒会、采购目录与离职工程师口中的碎片，终会在香港拼成一张足以指导生产的蓝图。',
      {'pp': '15', 'reserves': '0.06'}, {'competition': '0.025', 'supervisor': '1'},
      ('TNO_improve_research_facilities_low',), icon='GFX_decision_generic_intelligence_exchange'),
    E(0, 'tariff_lobby', '游说欧美监管机构减免出口关税',
      '华盛顿、日耳曼尼亚与米兰的关税表格各有一套晦涩语法，而广东商会恰好熟悉每一种。几场闭门午宴和一叠措辞谨慎的备忘录，便可能让一行税号变得对我们格外宽容。',
      {'pp': '20', 'stage': '1.5'}, {'scale': '5', 'gdp': '0.0015'},
      ('TNO_improve_admin_efficiency_low',), icon='GFX_decision_generic_trade'),
    E(0, 'court_dissidents', '与各国科技界异见者暗通款曲',
      '每个技术体系都会把一批不合时宜的天才挤到边缘：预算被砍的研究员、晋升无望的工程师，以及看厌了保密协议的项目主管。广东不必认同他们的政治，只需要买下他们尚未被重视的知识。',
      {'money': '0.08', 'stability': '0.01'}, {'competition': '0.03', 'scale': '4'},
      ('TNO_improve_academic_base_low',), icon='GFX_decision_generic_research'),
    E(0, 'friendly_expositions', '赞助友好国家举办半导体展会',
      '一座灯火通明的展馆可以把枯燥的晶圆参数包装成现代生活的许诺。让广东企业站在最显眼的位置，也让合作国的记者相信，他们亲眼见证的是未来，而不是一场精心核算过的推销。',
      {'money': '0.10', 'pp': '15'}, {'competition': '0.02', 'scale': '6', 'stability': '0.005'},
      ('TNO_improve_industrial_expertise_low',), icon='GFX_decision_generic_propaganda'),
    E(0, 'shell_companies', '设立海外皮包公司与技术转运前哨',
      '禁运制度依赖纸面上的终点，而纸面终点可以是一间只有信箱、电话和名义董事的公司。我们将沿几条彼此隔离的贸易路线布置前哨，让敏感设备在抵达珠江前先拥有一段体面的身世。',
      {'pp': '35', 'reserves': '0.25'}, {'scale': '18', 'gdp': '0.003'},
      ('TNO_improve_admin_efficiency_med',), stage=1, icon='GFX_decision_generic_business_deal'),
    E(0, 'smuggle_blueprints', '越境走私关键图纸',
      '机器可以被海关扣押，尺寸公差和工艺窗口却能藏在缩微胶片、维修手册与工程师的记忆里。专业人员将把这些图纸拆散、转译，再经数条互不相识的线路送回广东。',
      {'reserves': '0.30', 'command': '15'}, {'competition': '0.09', 'scale': '14'},
      ('TNO_improve_research_facilities_med',), stage=2, icon='GFX_decision_generic_intelligence_exchange'),
    E(0, 'embargo_waivers', '积极参与技术禁运豁免谈判',
      '走私能解决一台机器，却解决不了一整条产业链。广东必须以可靠供应商、低风险转口地和政治缓冲区的身份坐上谈判桌，把临时通融写成可重复使用的豁免条款。',
      {'pp': '45', 'stage': '3'}, {'competition': '0.07', 'gdp': '0.004', 'reserves': '0.12'},
      ('TNO_improve_admin_efficiency_med',), stage=3, icon='GFX_decision_generic_diplomatic_treaty'),
    E(0, 'public_diplomacy', '发起全球公共外交攻势',
      '当广东芯片出现在收音机、计算器与医院设备里，产地本身便应成为一种信誉。广告公司、商会和驻外机构将共同讲述一个无害而进步的广东，使监管者更难把封锁包装成道德义务。',
      {'pp': '50', 'reserves': '0.40'}, {'competition': '0.10', 'stability': '0.015', 'supervisor': '3'},
      ('TNO_improve_academic_base_med', 'TNO_improve_admin_efficiency_low'), stage=4,
      icon='GFX_decision_generic_propaganda'),
])

DECISIONS.extend([
    E(4, 'recruit_assembly_labor', '招募低成本劳动力进入流水线',
      '封装厂需要的不是少数明星工程师，而是成千上万双能在显微镜下重复同一动作的手。劳务机构将深入珠江两岸，以宿舍、计件工资和一张进城车票填满装配线。',
      {'manpower': '3500', 'reserves': '0.04'}, {'scale': '6', 'gdp': '0.001', 'stability': '0.005'},
      ('TNO_improve_admin_efficiency_low',), icon='GFX_decision_generic_manpower'),
    E(4, 'lower_piece_rates', '下调装配厂基础计件工资标准',
      '每一枚芯片上的工资微不足道，乘上数百万枚便足以改变报价。厂方会重订计件标准、扩大考核差距，并把由此产生的不满留给工会干事和戏院里的掌声处理。',
      {'audience': '3', 'stability': '0.01'}, {'scale': '7', 'reserves': '0.06'},
      ('TNO_improve_industrial_expertise_low',), icon='GFX_decision_generic_industry'),
    E(4, 'consumer_oem_orders', '承接民用电子产品代工',
      '计算器、收音机和廉价家电不需要最先进的芯片，却需要可靠而便宜的组装。把闲置工位交给大批量民用订单，可以训练工人，也能为更复杂的封装积累现金。',
      {'manpower': '3000'}, {'scale': '6', 'reserves': '0.07', 'gdp': '0.001'},
      ('TNO_improve_industrial_equipment_low',), icon='GFX_decision_generic_business_deal'),
    E(4, 'bonding_consumables', '采购高速引线键合消耗材料',
      '封装良率常常败在最不起眼的地方：一段不均匀的金丝、一块受潮的塑封料，或一枚磨损过度的劈刀。统一采购和批次检验能够让高速键合机少制造一些昂贵废品。',
      {'reserves': '0.06'}, {'scale': '4', 'competition': '0.02'},
      ('TNO_improve_industrial_expertise_low',), icon='GFX_decision_generic_industry'),
    E(4, 'dip_expansion', '规模化扩建DIP双列直插封装产线',
      '双列直插封装仍是七十年代电子工业最通用的语言。扩大冲压、键合、塑封和终测产能，能让广东用可靠的大批量交付占住从计算器到工业控制器的每一块电路板。',
      {'reserves': '0.35', 'manpower': '12000'}, {'scale': '26', 'audience': '1'},
      ('TNO_improve_industrial_equipment_med',), stage=1, icon='GFX_decision_generic_construct_civilian'),
    E(4, 'worker_housing', '建设计件工人配套社区与宿舍',
      '流水线不能在工人睡在通铺、每天跨城通勤时保持稳定。成片宿舍、食堂、诊所和托儿所既是社会工程，也是把廉价劳动力固定在工厂门口的生产设施。',
      {'reserves': '0.40', 'pp': '35'}, {'scale': '18', 'audience': '3', 'stability': '0.015'},
      ('TNO_improve_poverty_med', 'TNO_improve_admin_efficiency_low'), stage=2,
      icon='GFX_decision_generic_construct_civilian'),
    E(4, 'smt_pilot_line', '引入表面贴装技术自动化试制线',
      '表面贴装尚未取代通孔装配，却已经展示出更小、更快和更适合自动化的未来。我们将建立一条小批量试制线，在设备、焊膏和元件规格仍未统一时提前积累经验。',
      {'reserves': '0.55', 'audience': '2'}, {'scale': '22', 'competition': '0.10'},
      ('TNO_improve_industrial_equipment_high',), stage=3, icon='GFX_decision_generic_research'),
    E(4, 'qfp_testing_center', '升级四方扁平封装高针脚产线与测试中心',
      '日本企业已经开始用四方扁平封装容纳更多引脚，但高密度键合和终测仍会吞噬良率。广东将把精密冲压、视觉检查与自动测试集中起来，抢先把新封装变成可出口的常规产品。',
      {'reserves': '0.65', 'manpower': '20000'}, {'scale': '28', 'competition': '0.13', 'gdp': '0.005'},
      ('TNO_improve_industrial_expertise_high', 'TNO_improve_research_facilities_med'), stage=4,
      icon='GFX_decision_generic_research'),
])

DECISIONS.extend([
    E(5, 'liner_subsidies', '补贴电子产品专用班轮航线',
      '芯片体积很小，误船一周造成的损失却很大。政府将补贴固定舱位、恒温仓和优先装卸，让装满电子元件的货柜不再与矿石和廉价纺织品排同一条队。',
      {'reserves': '0.07'}, {'scale': '5', 'gdp': '0.0015'},
      ('TNO_improve_admin_efficiency_low',), icon='GFX_decision_generic_trade'),
    E(5, 'esd_packaging_standard', '推行防静电托盘与真空包装标准',
      '一批元件可能在离厂时完好，却在开箱前被静电和潮气悄悄杀死。统一托盘、干燥剂、真空袋与接地规程，会让广东货物抵达客户手中时仍像测试报告所写的那样工作。',
      {'pp': '15'}, {'competition': '0.025', 'scale': '4'},
      ('TNO_improve_industrial_expertise_low',), icon='GFX_decision_generic_document'),
    E(5, 'overland_transshipment', '开展转口贸易陆路走廊运输',
      '港口名单容易被封锁，跨境公路上的货单则更容易改写。广东商社将把敏感设备拆成普通零件，经数个自由港和陆路口岸转运，以时间换取更难追踪的来源。',
      {'pp': '20'}, {'scale': '6', 'reserves': '0.05'},
      ('TNO_improve_admin_efficiency_low',), icon='GFX_decision_generic_trade'),
    E(5, 'direct_distribution', '维护全球零部件直营分销网络',
      '卖出芯片只是第一步，客户还需要样品、替换件和懂得回答工程问题的人。由广东企业直接经营海外仓与技术销售，可以少分一层利润，也少受一层政治风险。',
      {'reserves': '0.08', 'pp': '10'}, {'scale': '5', 'reserves': '0.09'},
      ('TNO_improve_admin_efficiency_low',), icon='GFX_decision_generic_business_deal'),
    E(5, 'iso_container_coordination', '与德国协调ISO标准集装箱规格',
      '国际集装箱规格早已存在，真正的问题是铁路限界、码头吊具和货运单据能否在不同阵营之间顺畅衔接。与德国协调既有ISO规格的执行细节，将为广东货物打开一条更可预测的西向通道。',
      {'pp': '35'}, {'scale': '18', 'gdp': '0.003', 'reserves': '0.10'},
      ('TNO_improve_admin_efficiency_med',), stage=1, icon='GFX_decision_generic_diplomatic_treaty'),
    E(5, 'customs_fast_lane', '与美国建立电子元器件海关快速验放通道',
      '所谓快速通道不会免除检查，只会让预申报、抽检和保税转运在同一套表格里完成。若美国海关愿意承认广东企业的合规记录，交货周期便能从政治风险变成可计算的商业成本。',
      {'pp': '45', 'reserves': '0.30'}, {'scale': '22', 'gdp': '0.004'},
      ('TNO_improve_admin_efficiency_high',), stage=2, icon='GFX_decision_generic_diplomatic_treaty'),
    E(5, 'south_america_assembly', '在南美洲租赁电子产品加工厂',
      '当地装配可以绕过部分关税，也能让广东产品披上一层更容易进入美洲市场的产地。我们不会建设宏伟新城，只会租下现成厂房，把封装、终装和售后环节搬到消费者附近。',
      {'reserves': '0.55'}, {'scale': '28', 'gdp': '0.005'},
      ('TNO_improve_industrial_equipment_med',), stage=3, icon='GFX_decision_generic_construct_civilian'),
    E(5, 'strategic_component_buffer', '在共荣圈内建立战略元器件仓储缓冲网',
      '供应链最快的时候几乎看不见，断裂时却会让整座工厂停摆。分散在共荣圈港口与工业区的保税仓，将储存关键芯片、材料和备件，为战争、制裁或航运危机争取数月时间。',
      {'pp': '50', 'war': '0.02'}, {'scale': '30', 'stability': '0.015', 'reserves': '0.20'},
      ('TNO_improve_admin_efficiency_high', 'TNO_improve_industrial_expertise_low'), stage=4,
      icon='GFX_decision_generic_trade'),
])

DECISIONS.extend([
    E(3, 'optical_calibration', '光刻机高频光学校准与维护',
      '三微米线宽并不宽容镜头漂移、平台振动和灯源衰减。把校准从故障后的补救变成每班例行程序，会牺牲一点开机时间，却能换回更多真正可用的晶圆。',
      {'reserves': '0.08'}, {'competition': '0.03', 'scale': '3'},
      ('TNO_improve_research_facilities_low',), icon='GFX_decision_generic_research'),
    E(3, 'import_photoresist', '进口高纯度光刻胶化学制剂',
      '曝光设备再精密，也救不了成分漂移的光刻胶。贸易局将以医药和精细化工名义采购高纯正胶、显影剂与过滤材料，为下一批掩膜转移提供稳定化学基础。',
      {'reserves': '0.07', 'pp': '10'}, {'competition': '0.025', 'gdp': '0.001'},
      ('TNO_improve_research_facilities_low',), icon='GFX_decision_generic_trade'),
    E(3, 'buy_pellicles', '定期购置防尘薄膜',
      '一粒落在光罩上的尘埃会被忠实复制到整片晶圆。定期更换防尘薄膜与密封组件，是一项毫无戏剧性的支出，却能让工厂少向客户解释那些排列整齐的重复缺陷。',
      {'reserves': '0.05'}, {'competition': '0.02', 'audience': '0.5'},
      ('TNO_improve_industrial_equipment_low',), icon='GFX_decision_generic_industry'),
    E(3, 'expert_allowances', '发放光刻专家专项津贴',
      '能同时理解光学、化学和机械对准的专家比设备更难进口。专项津贴、住房与不问出处的研究预算，可以让他们暂时忽略广东的粗糙，也让东京相信我们仍尊重真正的技术。',
      {'reserves': '0.10', 'stage': '1'}, {'competition': '0.035', 'supervisor': '1'},
      ('TNO_improve_academic_base_low',), icon='GFX_decision_generic_research'),
    E(3, 'ccd_scale_up', 'CCD电荷耦合器件研发规模化',
      '科学院已经证明电荷可以沿硅片受控转移，接下来必须证明这种器件能按批次生产。建立小规模成像阵列试制线，会把一项新奇发明变成广东在传感器领域的第一张名片。',
      {'reserves': '0.45', 'supervisor': '2'}, {'competition': '0.12', 'gdp': '0.004', 'stability': '0.01'},
      ('TNO_improve_research_facilities_high', 'TNO_improve_academic_base_med'), stage=1,
      icon='GFX_decision_generic_research'),
    E(3, 'g_line_stepper', '引进高数值孔径g线步进式光刻机',
      '接触式曝光的极限已经逼近，逐片步进曝光则代表另一种生产秩序。我们将争取购入七十年代末最先进的g线设备，并把相对更高的数值孔径驯服在本地洁净室里。',
      {'reserves': '0.65', 'pp': '50'}, {'competition': '0.15', 'scale': '20'},
      ('TNO_improve_industrial_expertise_high',), stage=2, icon='GFX_decision_generic_research'),
    E(3, 'chrome_quartz_masks', '建设超净铬版石英光罩自主制造线',
      '只要关键光罩仍需进口，广东的每次设计修改就仍需获得他人许可。电子束制版、铬膜沉积与缺陷检查将被集中到一条超净制造线，使版图第一次真正留在我们手中。',
      {'reserves': '0.55', 'manpower': '18000'}, {'competition': '0.14', 'supervisor': '2'},
      ('TNO_improve_research_facilities_high',), stage=3, icon='GFX_decision_generic_industry'),
    E(3, 'excimer_alignment', '攻关准分子激光光源与亚微米级对准技术',
      '准分子激光仍是昂贵而不稳定的实验方向，亚微米对准更远未成为量产常识。正因如此，广东才应在竞争者尚未完成下注前建立原型平台，把下一代光刻所需的光源、材料与计量经验提前收入囊中。',
      {'reserves': '0.80', 'supervisor': '4'}, {'competition': '0.18', 'scale': '18', 'gdp': '0.006'},
      ('TNO_improve_research_facilities_high', 'TNO_improve_academic_base_high'), stage=4,
      icon='GFX_decision_generic_research'),
])

DECISIONS.extend([
    E(2, 'replenish_consumables', '补充基础晶圆耗材与化学试剂',
      '洁净室不会因为采购处的预算流程而停止消耗酸、溶剂、气体和石英器皿。建立滚动安全库存，可以让技术员少填几张停线报告，也能让观众暂时看见一条运转顺畅的生产线。',
      {'reserves': '0.06'}, {'scale': '4', 'audience': '0.5'},
      ('TNO_improve_industrial_equipment_low',), icon='GFX_decision_generic_industry'),
    E(2, 'paramilitary_shifts', '晶圆厂技术员准军事化排班',
      '扩散炉和真空设备不认识周末。把技术员编成固定班组、以准军事化方式交接故障与工艺记录，能减少最昂贵的空转时间；代价则由睡眠、家庭和耐心共同承担。',
      {'audience': '3', 'stability': '0.01'}, {'competition': '0.025', 'scale': '6'},
      ('TNO_improve_industrial_expertise_low',), icon='GFX_decision_generic_prepare_civil_war'),
    E(2, 'spc_control', '导入SPC良率统计控制系统',
      '良率不应等到成品测试才被发现。统计过程控制将把每一道工序的漂移画成控制图，让工程师在整批晶圆报废之前就知道哪台设备偏离了窗口。',
      {'pp': '15'}, {'competition': '0.03', 'reserves': '0.04'},
      ('TNO_improve_industrial_expertise_low',), icon='GFX_decision_generic_research'),
    E(2, 'japanese_military_orders', '承接日本军事电子管件代工专单',
      '军方订单规格繁琐、审查严苛，却能为闲置产线提供稳定现金流。只要广东愿意让一部分民用产能服从东京的优先级，监制便会把那些不够先进但数量庞大的器件交给我们。',
      {'war': '0.01'}, {'scale': '7', 'reserves': '0.08'},
      ('TNO_improve_industrial_equipment_low',), icon='GFX_decision_generic_military_industry'),
    E(2, 'class_1000_cleanroom', '建造千级超净洁净室',
      '三微米工艺不容许普通厂房里的灰尘。新的千级洁净区将配备分区气流、过滤系统和严格的更衣程序，使污染控制从工人的经验变成建筑本身的功能。',
      {'reserves': '0.40', 'manpower': '15000'}, {'competition': '0.08', 'scale': '18'},
      ('TNO_improve_research_facilities_med',), stage=1, icon='GFX_decision_generic_construct_civilian'),
    E(2, 'four_inch_wafer_line', '引入四英寸晶圆标准化生产线',
      '八英寸晶圆仍属于未来，而四英寸已经足够迫使整座工厂重新学习搬运、曝光与炉管装载。标准化这条产线，将让广东比区域竞争者更早获得大直径晶圆的规模优势。',
      {'reserves': '0.55', 'pp': '45'}, {'scale': '28', 'competition': '0.10', 'gdp': '0.004'},
      ('TNO_improve_industrial_equipment_high',), stage=2, icon='GFX_decision_generic_industry'),
    E(2, 'implantation_and_oxidation', '攻关高能量离子注入与热氧化扩散',
      '离子注入不会立刻取代扩散炉，但能把掺杂剂送到更精确的位置。将注入、退火、热氧化与传统扩散编入同一套工艺窗口，才是把实验设备变成稳定生产能力的关键。',
      {'reserves': '0.45'}, {'competition': '0.12', 'scale': '20', 'supervisor': '1.5'},
      ('TNO_improve_research_facilities_high',), stage=3, icon='GFX_decision_generic_research'),
    E(2, 'automated_handling_fa', '部署自动晶圆传送与FA失效分析中心',
      '完全无人化的工厂仍是宣传画，但局部自动传送、批次追踪和集中失效分析已经触手可及。机器负责减少人为污染，工程师负责把每一枚坏芯片变成下一批产品的教训。',
      {'reserves': '0.65', 'supervisor': '3'}, {'competition': '0.14', 'scale': '25'},
      ('TNO_improve_industrial_expertise_high', 'TNO_improve_research_facilities_low'), stage=4,
      icon='GFX_decision_generic_research'),
])

DECISIONS.extend([
    E(1, 'buy_crude_silicon', '采购工业级粗硅原料',
      '电子级硅的起点并不体面：煤、电与成吨的工业粗硅。与其等待现货市场抬价，不如由贸易局提前锁定东南亚和共荣圈矿冶企业的余量，先让提纯炉吃饱。',
      {'reserves': '0.05'}, {'scale': '4', 'gdp': '0.001'},
      ('TNO_improve_industrial_equipment_low',), icon='GFX_decision_generic_mining'),
    E(1, 'smelter_overtime', '推行硅冶炼厂加班班次',
      '电弧炉停下一小时，后面的晶圆厂就会少一批原料。管理层可以把检修、换班与休息压缩到报表允许的最低限度；至于炉前工人的抱怨，宣传部门自会称之为产业升级必须支付的代价。',
      {'audience': '2', 'stability': '0.005'}, {'scale': '6', 'reserves': '0.04'},
      ('TNO_improve_industrial_expertise_low',), icon='GFX_decision_generic_industry'),
    E(1, 'power_subsidy', '国家电网特供高耗能电费补贴',
      '多晶硅提纯消耗的电力足以让财政官员心悸，也足以让工厂在普通电价下停摆。政府将以战略工业负荷的名义安排专线和阶梯补贴，把亏损留在电网账本，把产量留在企业报表。',
      {'reserves': '0.09', 'pp': '10'}, {'scale': '7', 'gdp': '0.0015'},
      ('TNO_improve_industrial_equipment_low',), icon='GFX_decision_generic_electricity'),
    E(1, 'export_low_grade_products', '对东南亚出口低端硅基产物',
      '并非每一炉产品都配得上进入集成电路。把不够纯的批次加工成合金、耐火材料和普通电子耗材，再装船销往价格敏感的市场，至少能让废品变成现金。',
      {'manpower': '2500'}, {'scale': '5', 'reserves': '0.05'},
      ('TNO_improve_admin_efficiency_low',), icon='GFX_decision_generic_trade'),
    E(1, 'polysilicon_plant', '扩建电子级多晶硅提纯厂',
      '实验室里的高纯样品无法喂饱工业体系。新的氯硅烷提纯与沉积车间将把电子级多晶硅变成连续产物，并以专门培训的工人维持那些容不得半点污染的管线。',
      {'reserves': '0.35', 'manpower': '12000'}, {'scale': '25', 'gdp': '0.004'},
      ('TNO_improve_industrial_equipment_med',), stage=1, icon='GFX_decision_generic_construct_civilian'),
    E(1, 'czochralski_growth', '引进直拉法单晶硅棒技术',
      '多晶硅只是原料，稳定的单晶才是工业能力。我们将购入直拉炉、籽晶控制和氧含量测定工艺，再让本地工程师把进口参数改造成广东能够重复执行的生产纪律。',
      {'reserves': '0.30', 'pp': '35'}, {'competition': '0.08', 'scale': '15'},
      ('TNO_improve_research_facilities_med',), stage=2, icon='GFX_decision_generic_research'),
    E(1, 'quartz_monopoly', '垄断高纯度石英矿源',
      '坩埚里的一点杂质足以毁掉整根晶棒。商社将以长期包销、设备换矿和政治担保锁住最可靠的高纯石英来源；监制或许不喜欢这种排他手段，但他们会喜欢稳定交付。',
      {'reserves': '0.40', 'supervisor': '2'}, {'scale': '24', 'gdp': '0.004', 'stability': '0.01'},
      ('TNO_improve_industrial_expertise_med',), stage=3, icon='GFX_decision_generic_mining'),
    E(1, 'four_inch_substrates', '构建四英寸硅单晶衬底标准化产线',
      '三英寸晶圆仍能生产，但四英寸衬底可以在每次曝光中容纳更多芯片。切片、倒角、研磨与抛光设备将按统一规格重排，使广东在七十年代末真正拥有一条大直径晶圆材料线。',
      {'reserves': '0.55', 'pp': '45'}, {'competition': '0.10', 'scale': '30', 'reserves': '0.18'},
      ('TNO_improve_industrial_equipment_high', 'TNO_improve_research_facilities_low'), stage=4,
      icon='GFX_decision_generic_industry'),
])


COST_ORDER = (
    'pp', 'reserves', 'money', 'stage', 'supervisor', 'audience',
    'stability', 'war', 'command', 'manpower',
)
THEATER_EFFECT_KINDS = frozenset({'stage', 'supervisor', 'audience'})
THEATER_EFFECT_MULTIPLIER = Decimal('2')
EPS_HUNDREDTH = Decimal('0.01')
EPS_TEN_THOUSANDTH = Decimal('0.0001')
EPS_ONE = Decimal('1')


def number(raw: str | Decimal) -> str:
    value = Decimal(raw)
    rendered = format(value, 'f')
    if '.' in rendered:
        rendered = rendered.rstrip('0').rstrip('.')
    return rendered or '0'


def effective_value(kind: str, raw: str | Decimal) -> Decimal:
    value = Decimal(raw)
    if kind in THEATER_EFFECT_KINDS:
        value *= THEATER_EFFECT_MULTIPLIER
    return value


def threshold(raw: str | Decimal, epsilon: str | Decimal) -> str:
    return number(Decimal(raw) - Decimal(epsilon))


def previous_stage_flag(decision: Decision) -> str | None:
    if decision.stage <= 1:
        return None
    previous = next(
        item for item in DECISIONS
        if item.group == decision.group and item.stage == decision.stage - 1
    )
    return f'{previous.key}_complete'


def next_stage_decision(decision: Decision) -> Decision | None:
    if decision.stage <= 0 or decision.stage >= 4:
        return None
    return next(
        item for item in DECISIONS
        if item.group == decision.group and item.stage == decision.stage + 1
    )


def render_cost_trigger(decision: Decision) -> list[str]:
    checks: list[str] = []
    for cost in COST_ORDER:
        if cost not in decision.costs:
            continue
        value = effective_value(cost, decision.costs[cost])
        if cost == 'pp':
            checks.append(f'has_political_power > {threshold(value, EPS_HUNDREDTH)}')
        elif cost in {'reserves', 'money'}:
            continue
        elif cost == 'stage':
            maximum_corruption = number(Decimal('100.01') - Decimal(value))
            checks.append(
                f'check_variable = {{ GNG_corruption_var < {maximum_corruption} }}'
            )
        elif cost == 'supervisor':
            checks.append(
                f'check_variable = {{ GNG_Japan_Approval > {threshold(value, EPS_HUNDREDTH)} }}'
            )
        elif cost == 'audience':
            checks.append(
                f'check_variable = {{ GNG_China_Opinion > {threshold(value, EPS_HUNDREDTH)} }}'
            )
        elif cost == 'stability':
            checks.append(f'has_stability > {threshold(value, EPS_TEN_THOUSANDTH)}')
        elif cost == 'war':
            checks.append(f'has_war_support > {threshold(value, EPS_TEN_THOUSANDTH)}')
        elif cost == 'command':
            checks.append(f'command_power > {threshold(value, EPS_HUNDREDTH)}')
        elif cost == 'manpower':
            checks.append(f'manpower > {threshold(value, EPS_ONE)}')
        else:
            raise ValueError(f'unsupported cost: {cost}')
    return checks or ['always = yes']


def render_cost_effects(decision: Decision) -> tuple[list[str], list[str]]:
    hidden: list[str] = []
    visible: list[str] = []
    for cost in COST_ORDER:
        if cost not in decision.costs:
            continue
        value = effective_value(cost, decision.costs[cost])
        if cost == 'pp':
            hidden.append(f'add_political_power = -{number(value)}')
        elif cost in {'reserves', 'money'}:
            money_effects = [
                f'set_temp_variable = {{ temp_econ_spending_amount = {number(value)} }}',
                'econ_spend_money_once_effect_raw_money = yes',
            ]
            hidden.extend(money_effects)
            visible.extend([
                'effect_tooltip = {',
                *indented(money_effects, 4),
                '}',
            ])
        elif cost == 'stage':
            visible.extend([
                f'set_temp_variable = {{ DOP_SCW_stage_integrity_change = -{number(value)} }}',
                'DOP_SCW_change_stage_integrity = yes',
            ])
        elif cost == 'supervisor':
            visible.extend([
                f'set_temp_variable = {{ DOP_SCW_supervisor_attitude_change = -{number(value)} }}',
                'DOP_SCW_change_supervisor_attitude = yes',
            ])
        elif cost == 'audience':
            visible.extend([
                f'set_temp_variable = {{ DOP_SCW_audience_patience_change = -{number(value)} }}',
                'DOP_SCW_change_audience_patience = yes',
            ])
        elif cost == 'stability':
            effect = f'add_stability = -{number(value)}'
            hidden.append(effect)
            visible.extend(['effect_tooltip = {', f'    {effect}', '}'])
        elif cost == 'war':
            effect = f'add_war_support = -{number(value)}'
            hidden.append(effect)
            visible.extend(['effect_tooltip = {', f'    {effect}', '}'])
        elif cost == 'command':
            effect = f'add_command_power = -{number(value)}'
            hidden.append(effect)
            visible.extend(['effect_tooltip = {', f'    {effect}', '}'])
        elif cost == 'manpower':
            effect = f'add_manpower = -{number(value)}'
            hidden.append(effect)
            visible.extend(['effect_tooltip = {', f'    {effect}', '}'])
        else:
            raise ValueError(f'unsupported cost: {cost}')
    return hidden, visible


def render_complete_effect(decision: Decision) -> list[str]:
    hidden, visible = render_cost_effects(decision)
    lines: list[str] = []
    if hidden:
        lines.extend([
            'hidden_effect = {',
            *indented(hidden, 4),
            '}',
        ])
    lines.extend(visible)
    return lines


def render_reward_effects(decision: Decision) -> list[str]:
    effects: list[str] = []
    scale = decision.rewards.get('scale', '0')
    competition = decision.rewards.get('competition', '0')
    if scale != '0' and competition != '0':
        effects.extend([
            'set_temp_variable = { faction_id_t = 1 }',
            f'set_temp_variable = {{ DOP_SCW_production_scale_change = {number(scale)} }}',
            f'set_temp_variable = {{ DOP_SCW_competition_change = {number(competition)} }}',
            'DOP_SCW_change_production_and_competition = yes',
        ])
    elif scale != '0':
        effects.extend([
            'set_temp_variable = { faction_id_t = 1 }',
            f'set_temp_variable = {{ change_t = {number(scale)} }}',
            'SCW_production_scale_increase = yes',
        ])
    elif competition != '0':
        effects.extend([
            'set_temp_variable = { faction_id_t = 1 }',
            f'set_temp_variable = {{ change_t = {number(competition)} }}',
            'SCW_compatibility_increase = yes',
        ])
    gdp_reward = decision.rewards.get('gdp')
    if gdp_reward is not None:
        effects.extend([
            f'set_temp_variable = {{ gdp_growth_temp = {number(Decimal(gdp_reward) * 100)} }}',
            'econ_gdp_growth_change = yes',
        ])
    reserves_reward = decision.rewards.get('reserves')
    if reserves_reward is not None:
        effects.extend([
            f'set_temp_variable = {{ money_reserves_temp = {number(reserves_reward)} }}',
            'econ_money_reserves_change_raw_money = yes',
        ])
    stability_reward = decision.rewards.get('stability')
    if stability_reward is not None:
        effects.append(f'add_stability = {number(stability_reward)}')
    supervisor_reward = decision.rewards.get('supervisor')
    if supervisor_reward is not None:
        effects.extend([
            f'set_temp_variable = {{ DOP_SCW_supervisor_attitude_change = {number(effective_value("supervisor", supervisor_reward))} }}',
            'DOP_SCW_change_supervisor_attitude = yes',
        ])
    audience_reward = decision.rewards.get('audience')
    if audience_reward is not None:
        effects.extend([
            f'set_temp_variable = {{ DOP_SCW_audience_patience_change = {number(effective_value("audience", audience_reward))} }}',
            'DOP_SCW_change_audience_patience = yes',
        ])
    stage_reward = decision.rewards.get('stage')
    if stage_reward is not None:
        effects.extend([
            f'set_temp_variable = {{ DOP_SCW_stage_integrity_change = {number(effective_value("stage", stage_reward))} }}',
            'DOP_SCW_change_stage_integrity = yes',
        ])
    for helper in decision.applied_socdev:
        effects.append(f'{helper} = yes')
    if decision.stage:
        effects.extend([
            'hidden_effect = {',
            f'    set_country_flag = {decision.key}_complete',
            '}',
        ])
        following = next_stage_decision(decision)
        if following is not None:
            effects.append(f'{following.unlock_effect} = yes')
    return effects


def indented(lines: list[str], spaces: int) -> list[str]:
    prefix = ' ' * spaces
    return [f'{prefix}{line}' for line in lines]


def render_decision(decision: Decision) -> list[str]:
    icon = decision.icon if decision.icon in SAFE_DECISION_ICONS else 'GFX_decision_GNG_generic'
    visible = [
        'has_country_flag = DOP_SCW_decisions_unlocked',
        f'has_country_flag = {decision.unlock_flag}',
        'check_variable = { TNO_BoP_SelectedTab = token:BoP_Tab_DOPSiliconCW }',
        f'check_variable = {{ selected_decision_tabs_id = {1 if decision.group == 0 else 2} }}',
    ]
    if decision.group:
        visible.append(
            f'check_variable = {{ chain_part_selected = {decision.group} }}'
        )
    if decision.group == 3:
        visible.append('has_country_flag = DOP_SCW_CCD_research_complete')
    prior_flag = previous_stage_flag(decision)
    if prior_flag:
        visible.append(f'has_country_flag = {prior_flag}')

    available = [
        'has_country_flag = DOP_SCW_decisions_unlocked',
        f'has_country_flag = {decision.unlock_flag}',
    ]
    if decision.group == 3:
        available.append('has_country_flag = DOP_SCW_CCD_research_complete')
    if prior_flag:
        available.append(f'has_country_flag = {prior_flag}')

    lines = [
        f'    {decision.key} = {{',
        f'        icon = {icon}',
        '        allowed = { original_tag = GNG }',
        '        visible = {',
        *indented(visible, 12),
        '        }',
        '        available = {',
        *indented(available, 12),
        '        }',
        f'        custom_cost_text = {decision.key}_cost',
        '        custom_cost_trigger = {',
        *indented(render_cost_trigger(decision), 12),
        '        }',
        f'        days_remove = {30 if decision.repeatable else 365}',
    ]
    if decision.repeatable:
        lines.append('        days_re_enable = 90')
    else:
        lines.append('        fire_only_once = yes')
    lines.extend([
        '        complete_effect = {',
        *indented(render_complete_effect(decision), 12),
        '        }',
        '        remove_effect = {',
        *indented(render_reward_effects(decision), 12),
        '        }',
        '        ai_will_do = { factor = 0 }',
        '    }',
    ])
    return lines


def validate_data() -> None:
    keys = [decision.key for decision in DECISIONS]
    assert len(DECISIONS) == 48
    assert len(keys) == len(set(keys))
    assert all(not item.title.startswith(('阶段一：', '阶段二：', '阶段三：', '阶段四：')) for item in DECISIONS)
    for group in range(6):
        group_decisions = [item for item in DECISIONS if item.group == group]
        assert len(group_decisions) == 8
        assert sum(item.repeatable for item in group_decisions) == 4
        assert sorted(item.stage for item in group_decisions if item.stage) == [1, 2, 3, 4]


def build_decisions() -> str:
    validate_data()
    lines = [
        '# Generated by tools/generate_dop_scw_decisions.py. Do not edit by hand.',
        '# The race page is tab 1; industry-chain buttons 1-5 are tab 2.',
        '',
        'GNG_SiliconCW_category = {',
    ]
    for group in range(6):
        lines.extend([
            '',
            f'    # {GROUP_KEYS[group]}',
        ])
        group_decisions = [item for item in DECISIONS if item.group == group]
        for decision in sorted(group_decisions, key=lambda item: (item.stage > 0, item.stage)):
            lines.extend(render_decision(decision))
            lines.append('')
    lines.append('}')
    return '\n'.join(lines).rstrip() + '\n'


def build_unlock_effects() -> str:
    validate_data()
    lines = [
        '# Generated by tools/generate_dop_scw_decisions.py. Do not edit by hand.',
        '# Each SCW decision has an independent unlock flag and tooltip.',
        '',
    ]
    for decision in DECISIONS:
        lines.extend([
            f'{decision.unlock_effect} = {{',
            '    if = {',
            f'        limit = {{ NOT = {{ has_country_flag = {decision.unlock_flag} }} }}',
            f'        custom_effect_tooltip = {decision.unlock_tooltip}',
            '        hidden_effect = {',
            f'            set_country_flag = {decision.unlock_flag}',
            '        }',
            '    }',
            '}',
            '',
        ])
    initial_decisions = [
        decision for decision in DECISIONS
        if decision.repeatable or decision.stage == 1
    ]
    lines.extend([
        '# Normal activation opens both SCW pages and silently unlocks only',
        '# repeatable decisions plus the first milestone of each annual chain.',
        'DOP_SCW_activate_decision_system = {',
        '    hidden_effect = {',
        '        if = {',
        '            limit = { NOT = { has_country_flag = DOP_SCW_enabled } }',
        '            GNG_BOP_SCW_Initialize = yes',
        '        }',
        '        set_temp_variable = { decision_tabs_id = 1 }',
        '        GNG_SCW_add_tab = yes',
        '        set_temp_variable = { decision_tabs_id = 2 }',
        '        GNG_SCW_add_tab = yes',
        '        GNG_SCW_Initialize = yes',
        '        set_country_flag = DOP_SCW_decisions_unlocked',
    ])
    lines.extend(f'        set_country_flag = {decision.unlock_flag}' for decision in initial_decisions)
    lines.extend([
        '    }',
        '}',
        '',
    ])
    lines.extend([
        '# Debug-only bulk unlock: deliberately suppresses 48 tooltip lines.',
        'DOP_SCW_debug_unlock_all_decisions = {',
        '    hidden_effect = {',
    ])
    lines.extend(f'        set_country_flag = {decision.unlock_flag}' for decision in DECISIONS)
    lines.extend([
        '    }',
        '}',
    ])
    return '\n'.join(lines).rstrip() + '\n'


def money_label(raw: str) -> str:
    value = Decimal(raw)
    if value < 1:
        return f'{number(value * 1000)}M'
    return f'{number(value)}B'


def cost_component(kind: str, raw: str, blocked: bool) -> str:
    color = '§R' if blocked else '§Y'
    end = '§!'
    value = number(effective_value(kind, raw))
    if kind == 'pp':
        return f'£political_power_texticon {color}{value}{end}'
    if kind in {'reserves', 'money'}:
        return f'£GFX_green_dollar_sign {color}{money_label(raw)}{end}'
    if kind == 'stage':
        return f'£GFX_DOP_SCW_stage_integrity_texticon {color}{value}{end}'
    if kind == 'supervisor':
        return f'£GFX_DOP_SCW_supervisor_attitude_texticon {color}{value}%{end}'
    if kind == 'audience':
        return f'£GFX_DOP_SCW_audience_patience_texticon {color}{value}%{end}'
    if kind == 'stability':
        return f'£stability_texticon {color}{number(Decimal(raw) * 100)}%{end}'
    if kind == 'war':
        return f'£war_support_texticon {color}{number(Decimal(raw) * 100)}%{end}'
    if kind == 'command':
        return f'£command_power {color}{value}{end}'
    if kind == 'manpower':
        return f'£manpower_texticon {color}{int(Decimal(raw)):,}{end}'
    raise ValueError(f'unsupported cost: {kind}')


def escape_loc(text: str) -> str:
    return text.replace('\\', '\\\\').replace(chr(34), '\\' + chr(34))


def loc_line(key: str, value: str) -> str:
    quote = chr(34)
    return f' {key}:0 {quote}{escape_loc(value)}{quote}'


def build_localisation() -> str:
    validate_data()
    lines = [
        'l_simp_chinese:',
        loc_line(
            'DOP_SCW_audience_patience_change_positive_tt',
            '£GFX_DOP_SCW_audience_patience_texticon §M观众的耐心§!将§G提升§!§Y[?DOP_SCW_audience_patience_change_abs|1]%§!。',
        ),
        loc_line(
            'DOP_SCW_audience_patience_change_negative_tt',
            '£GFX_DOP_SCW_audience_patience_texticon §M观众的耐心§!将§R下降§!§Y[?DOP_SCW_audience_patience_change_abs|1]%§!。',
        ),
        loc_line(
            'DOP_SCW_supervisor_attitude_change_positive_tt',
            '£GFX_DOP_SCW_supervisor_attitude_texticon §j监制的态度§!将§G提升§!§Y[?DOP_SCW_supervisor_attitude_change_abs|1]%§!。',
        ),
        loc_line(
            'DOP_SCW_supervisor_attitude_change_negative_tt',
            '£GFX_DOP_SCW_supervisor_attitude_texticon §j监制的态度§!将§R下降§!§Y[?DOP_SCW_supervisor_attitude_change_abs|1]%§!。',
        ),
        loc_line(
            'DOP_SCW_stage_integrity_change_positive_tt',
            '£GFX_DOP_SCW_stage_integrity_texticon §R舞台完整度§!将§G提升§!§Y[?DOP_SCW_stage_integrity_change_abs|1]§!。',
        ),
        loc_line(
            'DOP_SCW_stage_integrity_change_negative_tt',
            '£GFX_DOP_SCW_stage_integrity_texticon §R舞台完整度§!将§R下降§!§Y[?DOP_SCW_stage_integrity_change_abs|1]§!。',
        ),
        loc_line(
            'DOP_SCW_production_and_competition_increase_tt',
            '§Y[GetChangedFactionNAME]§!的§C产业规模§!将§G提升§!§Y[?DOP_SCW_production_scale_change]§!，§m竞争力§!将§G提升§!§Y[?DOP_SCW_competition_change|2%]§!。',
        ),
        loc_line(
            'DOP_SCW_decisions_unlocked',
            '§W三微米冷战§!决议系统已经§G解锁§!。',
        ),
        loc_line(
            'DOP_SCW_CCD_research_complete',
            '§mCCD技术研发§!已经§G完成§!。',
        ),
        loc_line(
            'DOP_SCW_enabled',
            '§W三微米冷战§!界面已经§G启用§!。',
        ),
        loc_line(
            'DOP_SCW_off',
            '§W三微米冷战§!界面目前§R关闭§!。',
        ),
        loc_line(
            'DOP_SCW_initialized',
            '§W三微米冷战§!市场数据已经§G初始化§!。',
        ),
        loc_line(
            'GNG_dop_debug_unlock_SCW_decisions',
            '§MDOP调试§!：解锁三微米冷战决议',
        ),
        loc_line(
            'GNG_dop_debug_unlock_SCW_decisions_desc',
            '初始化三微米冷战市场数据，开放竞速与产业链页面，解锁全部48项独立决议，并临时满足CCD研发前置条件。',
        ),
        '',
    ]
    for group in range(6):
        lines.append(f' # {GROUP_KEYS[group]}')
        group_decisions = [item for item in DECISIONS if item.group == group]
        for decision in sorted(group_decisions, key=lambda item: (item.stage > 0, item.stage)):
            normal_cost = '  '.join(
                cost_component(kind, decision.costs[kind], False)
                for kind in COST_ORDER if kind in decision.costs
            )
            blocked_cost = '  '.join(
                cost_component(kind, decision.costs[kind], True)
                for kind in COST_ORDER if kind in decision.costs
            )
            lines.extend([
                loc_line(decision.key, decision.title),
                loc_line(f'{decision.key}_desc', decision.desc),
                loc_line(f'{decision.key}_cost', normal_cost),
                loc_line(f'{decision.key}_cost_blocked', blocked_cost),
                loc_line(
                    decision.unlock_flag,
                    f'£GFX_decision_icon_small §Y「${decision.key}$」§!决议已经§G解锁§!。',
                ),
                loc_line(
                    decision.unlock_tooltip,
                    f'§F£GFX_green_dollar_sign §W三微米冷战§!中的§Y「${decision.key}$」§!£GFX_decision_icon_small §D决议§!已经§G可用§!。§!',
                ),
            ])
            if decision.stage:
                lines.append(loc_line(
                    f'{decision.key}_complete',
                    f'£GFX_decision_icon_small §Y「${decision.key}$」§!决议已经§G完成§!。',
                ))
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def emit(path: Path, content: str, encoding: str, check: bool) -> bool:
    payload = content.encode(encoding)
    if check:
        if not path.exists() or path.read_bytes() != payload:
            print(f'OUT OF DATE: {path.relative_to(ROOT)}')
            return False
        print(f'OK: {path.relative_to(ROOT)}')
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    print(f'WROTE: {path.relative_to(ROOT)}')
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    ok = emit(DECISIONS_PATH, build_decisions(), 'utf-8', args.check)
    ok &= emit(LOCALISATION_PATH, build_localisation(), 'utf-8-sig', args.check)
    ok &= emit(UNLOCK_EFFECTS_PATH, build_unlock_effects(), 'utf-8', args.check)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
