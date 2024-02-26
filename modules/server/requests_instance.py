# Контроллеры http запросов
from modules.server.entity_controllers.article_controller import ArticleController
from modules.server.entity_controllers.custom_answer_controller import CustomAnswerController
from modules.server.entity_controllers.lead_controller import LeadBoardController
from modules.server.entity_controllers.quiz_controller import QuizController
from modules.server.entity_controllers.student_answer_controller import StudentAnswerController
from modules.server.entity_controllers.student_controller import StudentController
from modules.server.entity_controllers.task_controller import TaskController

student_con = StudentController()
article_con = ArticleController()
custom_answer_con = CustomAnswerController()
lead_con = LeadBoardController()
quiz_con = QuizController()
student_answer_con = StudentAnswerController()
task_con = TaskController()