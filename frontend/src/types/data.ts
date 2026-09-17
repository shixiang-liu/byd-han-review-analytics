export interface AnalysisWindow {
  startMonth: string;
  endMonth: string;
}

export interface AspectMetric {
  aspect: string;
  aspectCn: string;
  performance: number;
  sentimentMean: number;
}

export interface TopEffect {
  aspect: string;
  aspectCn: string;
  theta: number;
  ciLower: number;
  ciUpper: number;
}

export interface DashboardSummary {
  projectName: string;
  sampleCount: number;
  analysisWindow: AnalysisWindow;
  priorityItems: string[];
  strengthItems: string[];
  scoreSnapshot: AspectMetric[];
  topEffects: TopEffect[];
}

export interface TimelinePoint {
  month: string;
  count: number;
}

export interface BreakdownItem {
  label: string;
  count: number;
}

export interface ScoreCoverageItem {
  aspect: string;
  aspectCn: string;
  count: number;
  share: number;
}

export interface DataOverview {
  sampleCount: number;
  reviewTimeline: TimelinePoint[];
  modelBreakdown: BreakdownItem[];
  cityBreakdown: BreakdownItem[];
  priceBreakdown: BreakdownItem[];
  scoreCoverage: ScoreCoverageItem[];
}

export interface SentimentOverall {
  positiveMean: number;
  negativeMean: number;
}

export interface AspectSentimentMetric {
  aspect: string;
  aspectCn: string;
  performance: number;
  sentimentMean: number;
  scoreMean: number;
  nSentiment: number;
}

export interface MonthlyTrendPoint {
  month: string;
  space: number | null;
  driving: number | null;
  range: number | null;
  appearance: number | null;
  interior: number | null;
  value: number | null;
  smart: number | null;
}

export interface NegativeKeywordItem {
  keyword: string;
  rank: number;
  weight: number;
  keywordType: string;
}

export interface NegativeKeywordTheme {
  aspect: string;
  aspectCn: string;
  keywords: NegativeKeywordItem[];
}

export interface SentimentInsight {
  overallSentiment: SentimentOverall;
  aspectSentiment: AspectSentimentMetric[];
  monthlyTrend: MonthlyTrendPoint[];
  negativeKeywords: NegativeKeywordTheme[];
}

export interface IpaItem {
  aspect: string;
  aspectCn: string;
  performance: number;
  importance: number;
  quadrant: string;
  quadrantName: string;
  action: string;
  priorityScore: number;
  priorityRank: number;
}

export interface CausalEffectItem {
  aspect: string;
  aspectCn: string;
  theta: number;
  se: number;  // 标准误差，图表必需字段
  ciLower: number;
  ciUpper: number;
  pValue: number;  // p值，统计显著性
  nUsed: number;
}

export interface PenaltyRewardItem {
  aspect: string;
  classification: string;
  penaltyWeight: number;
  rewardWeight: number;
  performance: number;
  doi: number;
}

export interface InnovationPriorityItem {
  aspect: string;
  importance: number;
  performance: number;
  innovationZ: number;
  expectRate: number;
  negRate: number;
}

export interface DecisionAnalysis {
  ipaMatrix: IpaItem[];
  causalEffects: CausalEffectItem[];
  penaltyReward: PenaltyRewardItem[];
  innovationPriority: InnovationPriorityItem[];
}

export interface StrategyPriorityAction {
  aspect: string;
  aspectCn: string;
  priorityRank: number;
  action: string;
  keywords: string[];
}

export interface StrategyPowertrainComparison {
  segment: string;
  sampleSize: number;
  space: number;
  driving: number;
  range: number;
  appearance: number;
  interior: number;
  value: number;
  smart: number;
}

export interface StrategyCityTierComparison {
  segment: string;
  sampleSize: number;
  range: number;
  value: number;
  smart: number;
}

export interface StrategyPriceRangeComparison {
  segment: string;
  sampleSize: number;
  value: number;
  interior: number;
}

export interface StrategySegmentComparisons {
  powertrain: StrategyPowertrainComparison[];
  cityTier: StrategyCityTierComparison[];
  priceRange: StrategyPriceRangeComparison[];
}

export interface StrategySandbox {
  priorityActions: StrategyPriorityAction[];
  segmentComparisons: StrategySegmentComparisons;
}

// ===== Dashboard新增类型 =====

export interface DashboardMetrics {
  sampleCount: number;
  analysisDimensions: number;
  priorityIssues: number;
  actionCount: number;
  analysisWindow: {
    start: string;
    end: string;
  };
  projectName: string;
}

export interface QuadrantDefinition {
  name: string;
  description: string;
  color: string;
}

export interface IpaQuadrantData {
  items: IpaItem[];
  quadrantDefinitions: Record<string, QuadrantDefinition>;
}

export interface KeywordItem {
  aspect: string;
  aspectCn: string;
  rank: number;
  keyword: string;
  keywordRaw: string;
  tfidfScore: number;
  scoreType: string;
  keywordType: string;
}

export interface KeywordAnalysisData {
  keywords: KeywordItem[];
  byAspect: Record<string, KeywordItem[]>;
  totalCount: number;
}

export interface SentimentTrendPoint {
  month: string;
  year: number;
  monthNum: number;
  overall: number;
  aspects: Record<string, number>;
}

export interface SentimentTrendData {
  trend: SentimentTrendPoint[];
  aspects: string[];
  aspectNames: Record<string, string>;
  totalCount: number;
}

export interface CausalEffectData {
  effects: CausalEffectItem[];
  totalCount: number;
}

export interface PerformanceScoreItem {
  aspect: string;
  aspectCn: string;
  scoreMean: number;
  sentimentMean: number;
  nScore: number;
  nSentiment: number;
  scoreNorm: number;
  sentimentNorm: number;
  performance: number;
}

export interface PerformanceScoresData {
  items: PerformanceScoreItem[];
}

export interface RecommendationItem {
  aspect: string;
  aspectCn: string;
  quadrant: string;
  quadrantName: string;
  priorityRank: number;
  recommendation: string;
  keywords: string[];
}

export interface DecisionRecommendations {
  recommendations: RecommendationItem[];
  totalCount: number;
}

export interface PrcaRecommendationItem {
  aspect: string;
  penaltyWeight: number;
  rewardWeight: number;
  classification: string;
  performance: number;
  doi: number;
}

export interface PrcaRecommendations {
  recommendations: PrcaRecommendationItem[];
  totalCount: number;
}
