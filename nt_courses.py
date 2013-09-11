from django.utils import unittest
from ecomap.models import Course

class CourseTest(unittest.TestCase):
	def setUp(self):
	    a = Course(course_id="234", name="Test Course", description="Wonderful Test Course, see it run.")
	    b = Course(course_id="456", name="Another Course", description="Another Test Course, see it run.")
	    c = Course(course_id="789", name="Special Course", description="Special Test Course, see it run.")

	def test_unicode(self):
		pass

    def test_all_users(self):
		list_users = Course.objects.order_by('name')