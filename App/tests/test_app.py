import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import *
from App.models.commands import *
from App.controllers import *


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UnitTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    #User Unit Tests
    def test_new_user(self):
        user = User("ryan", "ryanpass")
        assert user.username == "ryan"

    def test_hashed_password(self):
        password = "ryanpass"
        hashed = generate_password_hash(password, method='sha256')
        user = User("ryan", password)
        assert user.password != password

    def test_check_password(self):
        password = "ryanpass"
        user = User("ryan", password)
        assert user.check_password(password)

    #Student Unit Tests
    def test_new_student(self):
      student = Student("james", "jamespass")
      assert student.username == "james"

    def test_student_get_json(self):
      student = Student("james", "jamespass")
      self.assertDictEqual(student.get_json(), {"id": None, "username": "james", "rating_score": 1200, "comp_count": 0, "curr_rank": 0})
    
    def test_student_join_team(self):
      student = Student("james", "jamespass")
      team = Team("Scrum Lords")
      student.teams.append(team)
      assert team in student.teams

    #Moderator Unit Tests
    def test_new_moderator(self):
      mod = Moderator("robert", "robertpass")
      assert mod.username == "robert"

    def test_moderator_get_json(self):
      mod = Moderator("robert", "robertpass")
      self.assertDictEqual(mod.get_json(), {"id":None, "username": "robert", "competitions": []})
    
    def test_moderator_add_competition(self):
      mod = Moderator("robert", "robertpass")
      competition = Competition("RunTime", datetime.now(), "Mona", 2, 30)
      mod.competitions.append(competition)
      assert competition in mod.competitions
    
    def test_duplicate_moderator_assignment(self):
      mod1 = create_moderator("debra", "debrapass")
      comp = create_competition(mod1.username, "Code Clash", "26-01-2024T11:00", "St. Augustine", 1, 20)
      result = add_mod(mod1.username, comp.name, "debra")
      self.assertIsNone(result)

    #Team Unit Tests
    def test_new_team(self):
      team = Team("Scrum Lords")
      assert team.name == "Scrum Lords"
    
    def test_team_get_json(self):
      team = Team("Scrum Lords")
      self.assertDictEqual(team.get_json(), {"id":None, "name":"Scrum Lords", "students": []})
    
    def test_team_add_student(self):
      team = Team("Code Wars")
      student = Student("kim", "pass123")
      team.students.append(student)
      assert student in team.students
    
    #Competition Unit Tests
    def test_new_competition(self):
      competition = Competition("RunTime", datetime.strptime("09-02-2024", "%d-%m-%Y"), "St. Augustine", 1, 25)
      assert competition.name == "RunTime" and competition.date.strftime("%d-%m-%Y") == "09-02-2024" and competition.location == "St. Augustine" and competition.level == 1 and competition.max_score == 25

    def test_competition_get_json(self):
      competition = Competition("RunTime", datetime.strptime("09-02-2024", "%d-%m-%Y"), "St. Augustine", 1, 25)
      self.assertDictEqual(competition.get_json(), {"id": None, "name": "RunTime", "date": "09-02-2024", "time": "12:00 AM", "location": "St. Augustine", "level": 1, "max_score": 25, "moderators": [], "teams": []})
    
    def test_competition_add_team(self):
      competition = Competition("RunTime", datetime.now(), "Barbados", 1, 100)
      team = Team("Code Wars")
      competition.teams.append(team)
      assert team in competition.teams

    #Notification Unit Tests
    def test_new_notification(self):
      notification = Notification(1, "Ranking changed!")
      assert notification.student_id == 1 and notification.message == "Ranking changed!"

    def test_notification_get_json(self):
      notification = Notification(1, "Ranking changed!")
      json_data = notification.get_json()
      self.assertEqual(json_data['student_id'], 1)
      self.assertEqual(json_data['notification'], "Ranking changed!")
      self.assertIn('timestamp', json_data)
  
    #CompetitionTeam Unit Tests
    def test_new_competition_team(self):
      competition_team = CompetitionTeam(1, 1)
      assert competition_team.comp_id == 1 and competition_team.team_id == 1

    def test_competition_team_update_points(self):
      competition_team = CompetitionTeam(1, 1)
      competition_team.update_points(15)
      assert competition_team.points_earned == 15

    def test_competition_team_update_rating(self):
      competition_team = CompetitionTeam(1, 1)
      competition_team.update_rating(12)
      assert competition_team.rating_score == 12

    def test_competition_team_get_json(self):
      competition_team = CompetitionTeam(1, 1)
      competition_team.update_points(15)
      competition_team.update_rating(12)
      self.assertDictEqual(competition_team.get_json(), {"id": None, "team_id": 1, "competition_id": 1, "points_earned": 15, "rating_score": 12})

    #CompetitionModerator Unit Tests
    def test_new_competition_moderator(self):
      competition_moderator = CompetitionModerator(1, 1)
      assert competition_moderator.comp_id == 1 and competition_moderator.mod_id == 1

    def test_competition_moderator_get_json(self):
      competition_moderator = CompetitionModerator(1, 1)
      self.assertDictEqual(competition_moderator.get_json(), {"id": None, "competition_id": 1, "moderator_id": 1})

    #StudentTeam Unit Tests
    def test_new_student_team(self):
      student_team = StudentTeam(1, 1)
      assert student_team.student_id == 1 and student_team.team_id == 1
    
    def test_student_team_get_json(self):
      student_team = StudentTeam(1, 1)
      self.assertDictEqual(student_team.get_json(), {"id": None, "student_id": 1, "team_id": 1})
    
    # RankHistory Unit Tests
    def test_new_rank_history(self):
      history = RankHistory(
          student_id=1,
          competition_id=1,
          rank=1,
          rating=1200.0
      )
      assert history.student_id == 1
      assert history.rank == 1
      assert history.rating == 1200.0

    # Command Unit Tests
    def test_create_competition_command(self):
      mod = Moderator("debra", "debrapass")
      db.session.add(mod)
      db.session.commit()
    
      cmd = CreateCompetitionCommand(moderator_id=mod.id)
      result = cmd.execute(
          mod_names="debra",
          comp_name="Code Wars",
          date="26-01-2024T11:00",
          location="Online",
          level=1,
          max_score=10
      )
      assert result is not None

    
    def test_update_leaderboard_command(self):
      comp = Competition("Code Wars", datetime.now(), "Kingston", 2, 50)
      team = Team("Scrum Lords")
      db.session.add_all([comp, team])
      db.session.commit()

      comp_team = CompetitionTeam(comp.id, team.id)
      db.session.add(comp_team)
      db.session.commit()

      cmd = UpdateLeaderboardCommand(moderator_id="1")
      leaderboard = cmd.execute()
      assert isinstance(leaderboard, list)
    
    def test_create_competition_command_with_invalid_moderator(self):
      cmd = CreateCompetitionCommand(moderator_id="1")  

      result = cmd.execute(
          mod_names="debra",  
          comp_name="Hackathon",
          date="01-01-2025",
          location="Virtual",
          level=2,
          max_score=50
      )
      assert result is None

'''
    Integration Tests
'''
class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    #Feature 1 Integration Tests
    def test1_create_competition(self):
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024T11:00", "St. Augustine", 2, 25)
      assert comp.name == "RunTime" and comp.date.strftime("%d-%m-%Y") == "29-03-2024" and comp.location == "St. Augustine" and comp.level == 2 and comp.max_score == 25

    def test2_create_competition(self):
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024T11:00", "St. Augustine", 2, 25)
      self.assertDictEqual(comp.get_json(), {"id": 1, "name": "RunTime", "date": "29-03-2024", "time": "11:00 AM", "location": "St. Augustine", "level": 2, "max_score": 25, "moderators": ["debra"], "teams": []})
      
    #Feature 2 Integration Tests
    def test1_add_results(self):
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024T11:00", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      students = [student1.username, student2.username, student3.username]
      team = add_team(mod.username, comp.name, "Runtime Terrors", students)
      comp_team = add_results(mod.username, comp.name, "Runtime Terrors", 15)
      assert comp_team.points_earned == 15
    
    def test2_add_results(self):
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024T11:00", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      students = [student1.username, student2.username, student3.username]
      add_team(mod.username, comp.name, "Runtime Terrors", students)
      comp_team = add_results(mod.username, comp.name, "Runtime Terrors", 15)
      students = [student1.username, student4.username, student5.username]
      team = add_team(mod.username, comp.name, "Scrum Lords", students)
      assert team == None
    
    def test3_add_results(self):
      mod1 = create_moderator("debra", "debrapass")
      mod2 = create_moderator("robert", "robertpass")
      comp = create_competition(mod1.username, "RunTime", "29-03-2024T11:00", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      students = [student1.username, student2.username, student3.username]
      team = add_team(mod2.username, comp.name, "Runtime Terrors", students)
      assert team == None

    #Feature 3 Integration Tests
    def test_display_student_info(self):
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024T11:00", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      students = [student1.username, student2.username, student3.username]
      team = add_team(mod.username, comp.name, "Runtime Terrors", students)
      comp_team = add_results(mod.username, comp.name, "Runtime Terrors", 15)
      update_ratings(mod.username, comp.name)
      UpdateLeaderboardCommand(moderator_id=None).execute()
      info = display_student_info("james")
      profile = info["profile"]
      self.assertEqual(profile["username"], "james")
      self.assertEqual(profile["comp_count"], 1)
      self.assertEqual(profile["curr_rank"], 1)
      self.assertGreaterEqual(profile["rating_score"], 1200) 
      self.assertIn("RunTime", info["competitions"])


    #Feature 4 Integration Tests
    def test_display_competition(self):
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024T11:00", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      student7 = create_student("isabella", "isabellapass")
      student8 = create_student("richard", "richardpass")
      student9 = create_student("jessica", "jessicapass")
      students1 = [student1.username, student2.username, student3.username]
      team1 = add_team(mod.username, comp.name, "Runtime Terrors", students1)
      comp_team1 = add_results(mod.username, comp.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      team2 = add_team(mod.username, comp.name, "Scrum Lords", students2)
      comp_team2 = add_results(mod.username, comp.name, "Scrum Lords", 12)
      students3 = [student7.username, student8.username, student9.username]
      team3 = add_team(mod.username, comp.name, "Beyond Infinity", students3)
      comp_team = add_results(mod.username, comp.name, "Beyond Infinity", 10)
      update_ratings(mod.username, comp.name)
      UpdateLeaderboardCommand(moderator_id=None).execute()
      self.assertDictEqual(comp.get_json(), {'id': 1, 'name': 'RunTime', 'date': '29-03-2024', "time": "11:00 AM", 'location': 'St. Augustine', 'level': 2, 'max_score': 25, 'moderators': ['debra'], 'teams': ['Runtime Terrors', 'Scrum Lords', 'Beyond Infinity']})

    #Feature 5 Integration Tests
    def test_display_rankings(self):
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "26-01-2024T11:00", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      students1 = [student1.username, student2.username, student3.username]
      team1 = add_team(mod.username, comp.name, "Runtime Terrors", students1)
      comp_team1 = add_results(mod.username, comp.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      team2 = add_team(mod.username, comp.name, "Scrum Lords", students2)
      comp_team2 = add_results(mod.username, comp.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp.name)
      UpdateLeaderboardCommand(moderator_id=None).execute()
      rankings = display_rankings()
      self.assertEqual(len(rankings), 6)
      self.assertEqual(rankings[0]["student"], "james")
      self.assertGreater(rankings[0]["rating score"], rankings[-1]["rating score"])
      for entry in rankings:
          self.assertIn("placement", entry)
          self.assertIn("student", entry)
          self.assertIn("rating score", entry)

    #Feature 6 Integration Tests
    def test1_display_notification(self):
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "26-01-2024T11:00", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      students1 = [student1.username, student2.username, student3.username]
      team1 = add_team(mod.username, comp.name, "Runtime Terrors", students1)
      comp_team1 = add_results(mod.username, comp.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      team2 = add_team(mod.username, comp.name, "Scrum Lords", students2)
      comp_team2 = add_results(mod.username, comp.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp.name)
      UpdateLeaderboardCommand(moderator_id=None).execute()

      messages = [n["Notification"] for n in display_notifications("james")["notifications"]]
      self.assertIn("RANK : 1. Congratulations on your first rank!", messages)

    def test2_display_notification(self):
      mod = create_moderator("debra", "debrapass")
      comp1 = create_competition(mod.username, "RunTime", "26-01-2024T11:00", "St. Augustine", 2, 25)
      comp2 = create_competition(mod.username, "Hacker Cup", "28-01-2024T11:00", "Macoya", 1, 30)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      students1 = [student1.username, student2.username, student3.username]
      add_team(mod.username, comp1.name, "Runtime Terrors", students1)
      add_results(mod.username, comp1.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      add_team(mod.username, comp1.name, "Scrum Lords", students2)
      add_results(mod.username, comp1.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp1.name)
      UpdateLeaderboardCommand(moderator_id=None).execute()

      students3 = [student1.username, student4.username, student5.username]
      add_team(mod.username, comp2.name, "Runtime Terrors", students3)
      add_results(mod.username, comp2.name, "Runtime Terrors", 15)
      students4 = [student2.username, student3.username, student6.username]
      add_team(mod.username, comp2.name, "Scrum Lords", students4)
      add_results(mod.username, comp2.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp2.name)
      UpdateLeaderboardCommand(moderator_id=None).execute()

      messages = [n["Notification"] for n in display_notifications("james")["notifications"]]
      self.assertIn("RANK : 1. Congratulations on your first rank!", messages)
      self.assertIn("RANK : 1. Well done! You retained your rank.", messages)


    def test3_display_notification(self):
      mod = create_moderator("debra", "debrapass")
      comp1 = create_competition(mod.username, "RunTime", "29-03-2024T11:00", "St. Augustine", 2, 25)
      comp2 = create_competition(mod.username, "Hacker Cup", "23-02-2024T11:00", "Macoya", 1, 20)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      students1 = [student1.username, student2.username, student3.username]
      add_team(mod.username, comp1.name, "Runtime Terrors", students1)
      add_results(mod.username, comp1.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      add_team(mod.username, comp1.name, "Scrum Lords", students2)
      add_results(mod.username, comp1.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp1.name)
      UpdateLeaderboardCommand(moderator_id=None).execute()

      students3 = [student1.username, student4.username, student5.username]
      add_team(mod.username, comp2.name, "Runtime Terrors", students3)
      add_results(mod.username, comp2.name, "Runtime Terrors", 20)
      students4 = [student2.username, student3.username, student6.username]
      add_team(mod.username, comp2.name, "Scrum Lords", students4)
      add_results(mod.username, comp2.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp2.name)
      UpdateLeaderboardCommand(moderator_id=None).execute()

      messages = [n["Notification"] for n in display_notifications("steven")["notifications"]]
      self.assertIn("RANK : 1. Congratulations on your first rank!", messages)
      self.assertIn("RANK : 4. Oh no! Your rank has went down.", messages)


    def test4_display_notification(self):
      mod = create_moderator("debra", "debrapass")
      comp1 = create_competition(mod.username, "RunTime", "29-03-2024T11:00", "St. Augustine", 2, 25)
      comp2 = create_competition(mod.username, "Hacker Cup", "23-02-2024T11:00", "Macoya", 1, 20)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      students1 = [student1.username, student2.username, student3.username]
      add_team(mod.username, comp1.name, "Runtime Terrors", students1)
      add_results(mod.username, comp1.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      add_team(mod.username, comp1.name, "Scrum Lords", students2)
      add_results(mod.username, comp1.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp1.name)
      UpdateLeaderboardCommand(moderator_id=None).execute()

      students3 = [student1.username, student4.username, student5.username]
      add_team(mod.username, comp2.name, "Runtime Terrors", students3)
      add_results(mod.username, comp2.name, "Runtime Terrors", 20)
      students4 = [student2.username, student3.username, student6.username]
      add_team(mod.username, comp2.name, "Scrum Lords", students4)
      add_results(mod.username, comp2.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp2.name)
      UpdateLeaderboardCommand(moderator_id=None).execute()

      messages = [n["Notification"] for n in display_notifications("mark")["notifications"]]
      self.assertIn("RANK : 4. Congratulations on your first rank!", messages)
      self.assertIn("RANK : 2. Congratulations! Your rank has went up.", messages)


    #Additional Integration Tests
    def test1_add_mod(self):
      mod1 = create_moderator("debra", "debrapass")
      mod2 = create_moderator("robert", "robertpass")
      comp = create_competition(mod1.username, "RunTime", "29-03-2024T11:00", "St. Augustine", 2, 25)
      assert add_mod(mod1.username, comp.name, mod2.username) != None
       
    def test2_add_mod(self):
      mod1 = create_moderator("debra", "debrapass")
      mod2 = create_moderator("robert", "robertpass")
      mod3 = create_moderator("raymond", "raymondpass")
      comp = create_competition(mod1.username, "RunTime", "29-03-2024T11:00", "St. Augustine", 2, 25)
      assert add_mod(mod2.username, comp.name, mod3.username) == None
    
    def test_student_list(self):
      mod = create_moderator("debra", "debrapass")
      comp1 = create_competition(mod.username, "RunTime", "29-03-2024T11:00", "St. Augustine", 2, 25)
      comp2 = create_competition(mod.username, "Hacker Cup", "23-02-2024T11:00", "Macoya", 1, 20)

      # Create students
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      add_team(mod.username, comp1.name, "Runtime Terrors", [student1.username, student2.username, student3.username])
      add_results(mod.username, comp1.name, "Runtime Terrors", 15)
      add_team(mod.username, comp1.name, "Scrum Lords", [student4.username, student5.username, student6.username])
      add_results(mod.username, comp1.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp1.name)
      UpdateLeaderboardCommand(moderator_id=None).execute()
      add_team(mod.username, comp2.name, "Runtime Terrors", [student1.username, student4.username, student5.username])
      add_results(mod.username, comp2.name, "Runtime Terrors", 20)
      add_team(mod.username, comp2.name, "Scrum Lords", [student2.username, student3.username, student6.username])
      add_results(mod.username, comp2.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp2.name)
      UpdateLeaderboardCommand(moderator_id=None).execute()
      students = get_all_students_json()
      students_sorted = sorted(students, key=lambda s: s["curr_rank"])
      self.assertEqual(students_sorted[0]["username"], "james")
      self.assertEqual(students_sorted[0]["curr_rank"], 1)
      for s in students:
          self.assertIn("username", s)
          self.assertIsInstance(s["rating_score"], float)
          self.assertGreaterEqual(s["rating_score"], 0)
          self.assertGreater(s["comp_count"], 0)
          self.assertGreater(s["curr_rank"], 0)


    def test_comp_list(self):
      mod = create_moderator("debra", "debrapass")
      comp1 = create_competition(mod.username, "RunTime", "29-03-2024T11:00", "St. Augustine", 2, 25)
      comp2 = create_competition(mod.username, "Hacker Cup", "23-02-2024T11:00", "Macoya", 1, 20)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      students1 = [student1.username, student2.username, student3.username]
      team1 = add_team(mod.username, comp1.name, "Runtime Terrors", students1)
      comp1_team1 = add_results(mod.username, comp1.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      team2 = add_team(mod.username, comp1.name, "Scrum Lords", students2)
      comp1_team2 = add_results(mod.username, comp1.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp1.name)
      UpdateLeaderboardCommand(moderator_id=None).execute()
      students3 = [student1.username, student4.username, student5.username]
      team3 = add_team(mod.username, comp2.name, "Runtime Terrors", students3)
      comp_team3 = add_results(mod.username, comp2.name, "Runtime Terrors", 20)
      students4 = [student2.username, student3.username, student6.username]
      team4 = add_team(mod.username, comp2.name, "Scrum Lords", students4)
      comp_team4 = add_results(mod.username, comp2.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp2.name)
      UpdateLeaderboardCommand(moderator_id=None).execute()
      self.assertListEqual(get_all_competitions_json(), [{"id": 1, "name": "RunTime", "date": "29-03-2024", "time": "11:00 AM", "location": "St. Augustine", "level": 2, "max_score": 25, "moderators": ["debra"], "teams": ["Runtime Terrors", "Scrum Lords"]}, {"id": 2, "name": "Hacker Cup", "date": "23-02-2024", "time": "11:00 AM", "location": "Macoya", "level": 1, "max_score": 20, "moderators": ["debra"], "teams": ["Runtime Terrors", "Scrum Lords"]}])
    
    def test_multiple_moderator_assignment(self):
      mod1 = create_moderator("debra", "debrapass")
      mod2 = create_moderator("robert", "robertpass")
      comp = create_competition(mod1.username, "Debug Duel", "20-05-2025T11:00", "St. Augustine", 2, 40)
      self.assertIsNotNone(comp)
      result = add_mod(mod1.username, comp.name, mod2.username)
      self.assertIsNotNone(result)
      updated_comp = Competition.query.filter_by(name="Debug Duel").first()
      mod_names = [mod.username for mod in updated_comp.moderators]
      self.assertIn("debra", mod_names)
      self.assertIn("robert", mod_names)
      json_data = updated_comp.get_json()
      self.assertIn("debra", json_data["moderators"])
      self.assertIn("robert", json_data["moderators"])

    def test_rank_history(self):
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "Rank Wars", "05-05-2025T11:00", "St. Augustine", 2, 50)
      students = [create_student("james", "jamespass"), create_student("steven", "stevenpass"), create_student("emily", "emilypass")]
      add_team(mod.username, comp.name, "Runtime Terrors", [s.username for s in students])
      add_results(mod.username, comp.name, "Runtime Terrors", 20)
      update_ratings(mod.username, comp.name)
      UpdateLeaderboardCommand(moderator_id=mod.id).execute()
      rank_history = RankHistory.query.filter_by(student_id=students[0].id).all()
      self.assertGreaterEqual(len(rank_history), 1)
      self.assertEqual(rank_history[0].competition_id, comp.id)

    def test_competition_cycle(self):
      mod = create_moderator("debra", "debrapass")
      create_cmd = CreateCompetitionCommand(moderator_id=mod.id)
      comp = create_cmd.execute(
          mod_names="debra",
          comp_name="Algo Clash",
          date="15-05-2025T11:00",
          location="Online",
          level=1,
          max_score=30
      )
      self.assertIsNotNone(comp)
      self.assertEqual(comp.name, "Algo Clash")
      s1 = create_student("james", "jamespass")
      s2 = create_student("steven", "stevenpass")
      s3 = create_student("emily", "emilypass")
      students_team1 = [s1.username, s2.username, s3.username]
      s4 = create_student("mark", "markpass")
      s5 = create_student("eric", "ericpass")
      s6 = create_student("ryan", "ryanpass")
      students_team2 = [s4.username, s5.username, s6.username]
      add_team(mod.username, comp.name, "Runtime Terrors", students_team1)
      add_results(mod.username, comp.name, "Runtime Terrors", 25)
      add_team(mod.username, comp.name, "Scrum Lords", students_team2)
      add_results(mod.username, comp.name, "Scrum Lords", 15)
      update_ratings(mod.username, comp.name)
      leaderboard = UpdateLeaderboardCommand(moderator_id=mod.id).execute()
      self.assertTrue(any(entry["student"] == "james" for entry in leaderboard))
      student_info = display_student_info("james")
      self.assertEqual(student_info["profile"]["comp_count"], 1)
      self.assertGreater(student_info["profile"]["rating_score"], 1200.0)
      notifications = display_notifications("james")["notifications"]
      messages = [n["Notification"] for n in notifications]
      self.assertTrue(any("RANK : 1" in msg for msg in messages))