from models.news import NewsAdd
from repositories.category_repository import CategoryRepository
from repositories.news_repository import NewsRepository
from utils.summurizer_utils import MultilingualSummarizer


class NewsService:
    news_repository: NewsRepository
    category_repository: CategoryRepository
    
    def __init__(self) -> None:
        self.news_repository = NewsRepository()
        self.category_repository = CategoryRepository()
        
    def add_news(self, news: NewsAdd) -> None:
        TRIGGER_WORDS_CATEGORIES: dict[str, list[str]] = {
            "Research": ["study", "research", "paper", "publication", "findings", "experiment", "scientific", "peer-reviewed", "hypothesis", "methodology", "data analysis", "academic", "scholarly"],
            "AI Tools": ["tool", "software", "platform", "application", "framework", "library", "API", "SDK", "plugin", "extension", "utility", "package", "module", "interface"],
            "Industry": ["enterprise", "business", "corporation", "industry", "market", "sector", "commercial", "manufacturing", "supply chain", "logistics", "retail", "finance", "automotive"],
            "Startups": ["startup", "venture", "funding", "seed round", "accelerator", "incubator", "founder", "pitch", "angel investor", "VC", "bootstrapped", "unicorn", "scaleup", "disrupt"],
            "Regulation": ["law", "regulation", "policy", "legislation", "compliance", "governance", "oversight", "standard", "guideline", "framework", "enforcement", "audit", "certification"],
            "Ethics": ["ethical", "bias", "fairness", "privacy", "transparency", "accountability", "responsibility", "trustworthy", "equity", "inclusion", "diversity", "sustainability", "human rights"],
            "Health": ["medical", "healthcare", "diagnosis", "treatment", "patient", "hospital", "biomedical", "clinical", "pharmaceutical", "telemedicine", "wearable", "genomics", "prognosis"],
            "Robotics": ["robot", "drone", "automation", "mechanical", "actuator", "sensor", "manipulator", "autonomous", "cobot", "exoskeleton", "swarm", "kinematics", "end effector"],
            "AGI": ["artificial general intelligence", "AGI", "superintelligence", "consciousness", "human-level AI", "cognitive architecture", "theory of mind", "self-awareness", "reasoning", "learning", "adaptation"],
            "NLP": ["natural language processing", "NLP", "language model", "translation", "sentiment analysis", "text generation", "speech recognition", "chatbot", "transformer", "tokenization", "parsing", "semantics"],
            "Computer Vision": ["computer vision", "image recognition", "object detection", "facial recognition", "visual perception", "segmentation", "classification", "feature extraction", "optical flow", "depth estimation", "pose estimation"],
            "AI Art": ["AI art", "generative art", "creative AI", "digital art", "neural style transfer", "DALL-E", "Stable Diffusion", "Midjourney", "GAN", "procedural generation", "algorithmic art", "computational creativity"],
            "Opinion": ["opinion", "perspective", "viewpoint", "analysis", "commentary", "editorial", "thoughts", "reflection", "critique", "review", "take", "position", "argument"]
        }
        
        for key, values in TRIGGER_WORDS_CATEGORIES:
            for value in values:
                if value in news.body:
                    news.categoryId = self.category_repository.get_or_create_category(key)
                    break
                
        news.body = MultilingualSummarizer().summarize(news.body)['summary']
        self.news_repository.add_news(news)
        