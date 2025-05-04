import unittest
from main import SnakeGame

class RegressionTests(unittest.TestCase):
    def setUp(self):
        self.game = SnakeGame()

    def test_initial_state(self):
        self.assertEqual(len(self.game.players), 0)
        self.assertEqual(len(self.game.scores), 0)
        self.assertIsInstance(self.game.food, tuple)

    def test_add_player(self):
        self.game.add_player("p1", "Player1")
        self.assertIn("p1", self.game.players)
        self.assertEqual(self.game.scores["p1"], 0)

    def test_move_and_food(self):
        self.game.add_player("p2", "Player2")
        start_head = self.game.players["p2"][0]
        self.game.food = (start_head[0]+1, start_head[1])
        self.game.move_player("p2", "right")
        self.assertEqual(self.game.scores["p2"], 1)

    def test_self_collision(self):
        self.game.add_player("p3", "Player3")
        pid = "p3"
        # Grow snake to length 4
        self.game.players[pid] = [(5,5),(4,5),(4,6),(5,6)]
        self.game.move_player(pid, "up")  # Move into itself
        self.assertTrue(self.game.game_over[pid])

    def test_wall_collision(self):
        self.game.add_player("p4", "Player4")
        pid = "p4"
        self.game.players[pid] = [(0,0)]
        self.game.move_player(pid, "left")  # Move out of bounds
        self.assertTrue(self.game.game_over[pid])

if __name__ == '__main__':
    unittest.main()
