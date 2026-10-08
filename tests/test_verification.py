import unittest
from PIL import Image
from verification import compare_images


class TestVerification(unittest.TestCase):

    def test_compare_identical_images(self):
        img = Image.new("RGB", (100, 100), color="red")
        res = compare_images(img, img)
        self.assertEqual(res["change_score"], 0.0)
        self.assertFalse(res["verified"])

    def test_compare_different_images(self):
        img1 = Image.new("RGB", (100, 100), color="black")
        img2 = Image.new("RGB", (100, 100), color="white")
        res = compare_images(img1, img2)
        self.assertEqual(res["change_score"], 1.0)
        self.assertTrue(res["verified"])

    def test_compare_invalid_input(self):
        with self.assertRaises(ValueError):
            compare_images(None, None)


if __name__ == "__main__":
    unittest.main()
