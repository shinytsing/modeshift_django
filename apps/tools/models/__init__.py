# 🏗️ 优化的模型导入结构 - 逐步分离legacy_models

# 基础模型
from .base_models import ToolUsageLog

# 聊天模型从chat_models导入
from .chat_models import ChatMessage, ChatRoom, ChatRoomMember, ChatNotification, HeartLinkRequest, MessageRead, UserOnlineStatus

# 日记相关模型（已分离）
from .diary_models import LifeDiaryEntry

# 健身模型从fitness_models导入
from .fitness_models import EnhancedExerciseWeightRecord, EnhancedFitnessStrengthProfile

# 暂时从legacy_models导入其他模型，逐步迁移
from .legacy_models import (  # 生活目标相关; 成就相关; 健身相关; Vanity/欲望相关; 旅游相关（已移至travel_models.py）; 工作搜索相关; PDF转换相关; 食物相关; 人际关系相关 - 已移至relationship_models.py; RelationshipTag, PersonProfile, Interaction, ImportantMoment,; RelationshipStatistics, RelationshipReminder,; 功能相关; 健身社区相关; NutriCoach Pro相关模型已隐藏; DietPlan, Meal, NutritionReminder, MealLog,; WeightTracking, FoodDatabase,; 船宝相关; 旅游目的地相关; 搭子相关; 其他
    AIDependencyMeter,
    BasedDevAvatar,
    BuddyEvent,
    BuddyEventChat,
    BuddyEventMember,
    BuddyEventMessage,
    BuddyEventReport,
    BuddyEventReview,
    BuddyUserProfile,
    CheckInAchievement,
    CheckInCalendar,
    CheckInStreak,
    CodeWorkoutSession,
    CoPilotCollaboration,
    DailyWorkoutChallenge,
    DesireDashboard,
    DesireFulfillment,
    DesireItem,
    ExerciseWeightRecord,
    ExhaustionProof,
    Feature,
    FeatureRecommendation,
    FitnessAchievement,
    FitnessCommunityComment,
    FitnessCommunityLike,
    FitnessCommunityPost,
    FitnessFollow,
    FitnessStrengthProfile,
    FitnessUserProfile,
    FitnessWorkoutSession,
    FoodHistory,
    FoodItem,
    FoodPhotoBinding,
    FoodPhotoBindingHistory,
    FoodRandomizationSession,
    FoodRandomizer,
    JobApplication,
    JobSearchProfile,
    JobSearchRequest,
    JobSearchStatistics,
    LifeGoal,
    LifeGoalProgress,
    LifeStatistics,
    PainCurrency,
    PDFConversionRecord,
    ShipBaoItem,
    ShipBaoMessage,
    ShipBaoReport,
    ShipBaoTransaction,
    ShipBaoUserProfile,
    SinPoints,
    Sponsor,
    TrainingPlan,
    TravelDestination,
    UserAchievement,
    UserFeaturePermission,
    UserFirstVisit,
    UserFitnessAchievement,
    VanityTask,
    VanityWealth,
    WorkoutDashboard,
)

# 从nutrition_models导入营养信息相关模型
from .nutrition_models import FoodNutrition, FoodNutritionHistory, FoodRandomizationLog, NutritionCategory

# 从relationship_models导入人际关系相关模型
from .relationship_models import (
    ImportantMoment,
    Interaction,
    PersonProfile,
    RelationshipReminder,
    RelationshipStatistics,
    RelationshipTag,
)

# 社交媒体模型（已分离）
from .social_media_models import (
    DouyinVideo,
    DouyinVideoAnalysis,
    SocialMediaNotification,
    SocialMediaPlatformConfig,
    SocialMediaSubscription,
)

# 塔罗牌模型从tarot_models导入
from .tarot_models import TarotCard, TarotCommunity, TarotCommunityComment, TarotEnergyCalendar, TarotReading, TarotSpread

# 旅游攻略模型从travel_models导入
from .travel_models import (
    TravelCity,
    TravelGuide,
    TravelGuideCache,
    TravelGuideUsage,
    TravelPost,
    TravelPostComment,
    TravelPostFavorite,
    TravelPostLike,
    TravelReview,
    UserGeneratedTravelGuide,
)

# 船宝二手交易模型从shipbao_models导入（暂时注释，避免与legacy_models冲突）
# from .shipbao_models import (
#     ShipBaoItem, ShipBaoItemImage, ShipBaoFavorite, ShipBaoInquiry,
#     ShipBaoTransaction, ShipBaoUserProfile
# )


# 导出所有模型类
__all__ = [
    # 基础模型
    "ToolUsageLog",
    # 社交媒体模型
    "SocialMediaSubscription",
    "SocialMediaNotification",
    "SocialMediaPlatformConfig",
    "DouyinVideoAnalysis",
    "DouyinVideo",
    # 塔罗牌模型
    "TarotCard",
    "TarotSpread",
    "TarotReading",
    "TarotEnergyCalendar",
    "TarotCommunity",
    "TarotCommunityComment",
    # 聊天模型
    "ChatRoom",
    "ChatMessage",
    "ChatRoomMember",
    "ChatNotification",
    "MessageRead",
    "UserOnlineStatus",
    "HeartLinkRequest",
    # 日记模型
    "LifeDiaryEntry",
    "LifeGoal",
    "LifeGoalProgress",
    "LifeStatistics",
    # 成就模型
    "UserAchievement",
    # 健身模型
    "FitnessWorkoutSession",
    "CodeWorkoutSession",
    "ExhaustionProof",
    "AIDependencyMeter",
    "CoPilotCollaboration",
    "DailyWorkoutChallenge",
    "PainCurrency",
    "WorkoutDashboard",
    "TrainingPlan",
    "FitnessUserProfile",
    "EnhancedFitnessStrengthProfile",
    "EnhancedExerciseWeightRecord",
    # NutriCoach Pro相关模型已隐藏
    # 'DietPlan',
    # 'Meal',
    # 'NutritionReminder',
    # 'MealLog',
    # 'WeightTracking',
    # 'FoodDatabase',
    "FitnessAchievement",
    "UserFitnessAchievement",
    "FitnessFollow",
    "ExerciseWeightRecord",
    "FitnessStrengthProfile",
    # 健身社区模型
    "FitnessCommunityPost",
    "FitnessCommunityComment",
    "FitnessCommunityLike",
    # 旅游模型
    "TravelGuide",
    "TravelGuideCache",
    "TravelReview",
    "TravelCity",
    "TravelPost",
    "TravelPostLike",
    "TravelPostFavorite",
    "TravelPostComment",
    "UserGeneratedTravelGuide",
    "TravelGuideUsage",
    # 食物模型
    "FoodRandomizer",
    "FoodItem",
    "FoodRandomizationSession",
    "FoodHistory",
    "FoodPhotoBinding",
    "FoodPhotoBindingHistory",
    # 营养信息模型
    "NutritionCategory",
    "FoodNutrition",
    "FoodNutritionHistory",
    "FoodRandomizationLog",
    # 签到模型
    "CheckInCalendar",
    "CheckInDetail",
    "CheckInStreak",
    "CheckInAchievement",
    # Vanity模型
    "DesireDashboard",
    "DesireItem",
    "DesireFulfillment",
    "VanityWealth",
    "SinPoints",
    "Sponsor",
    "VanityTask",
    "BasedDevAvatar",
    # 搭子模型
    "BuddyEvent",
    "BuddyEventMember",
    "BuddyEventChat",
    "BuddyEventMessage",
    "BuddyUserProfile",
    "BuddyEventReview",
    "BuddyEventReport",
    # 船宝模型
    "ShipBaoItem",
    "ShipBaoTransaction",
    "ShipBaoMessage",
    "ShipBaoUserProfile",
    "ShipBaoReport",
    # 旅游目的地模型
    "TravelDestination",
    # 人际关系模型
    "RelationshipTag",
    "PersonProfile",
    "Interaction",
    "ImportantMoment",
    "RelationshipStatistics",
    "RelationshipReminder",
    # 功能模型
    "Feature",
    "UserFeaturePermission",
    "FeatureRecommendation",
    "UserFirstVisit",
    # 工作搜索模型
    "JobSearchRequest",
    "JobApplication",
    "JobSearchProfile",
    "JobSearchStatistics",
    # PDF转换模型
    "PDFConversionRecord",
]
