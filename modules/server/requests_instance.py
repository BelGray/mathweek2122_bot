# Контроллеры http запросов
import configuration_instance
from modules.server.entity_controllers.article_controller import ArticleController
from modules.server.entity_controllers.custom_answer_controller import CustomAnswerController
from modules.server.entity_controllers.lead_controller import LeadBoardController
from modules.server.entity_controllers.quiz_controller import QuizController
from modules.server.entity_controllers.student_answer_controller import StudentAnswerController
from modules.server.entity_controllers.student_controller import StudentController
from modules.server.entity_controllers.task_controller import TaskController

url = configuration_instance.server_url + "/"

student_con = StudentController(url)
article_con = ArticleController(url)
custom_answer_con = CustomAnswerController(url)
lead_con = LeadBoardController(url)
quiz_con = QuizController(url)
student_answer_con = StudentAnswerController(url)
task_con = TaskController(url)