from django.utils import unittest
from ecomap.models import Ecouser, Ecomap
from django.contrib.auth.models import User


class EcomodelTest(unittest.TestCase):

    def setUp(self):
        self.a = User(first_name="first", last_name="student", username="fstudent", password="fstudent", email="fstudent@email.com")
        #self.ea = self.a.get_profile()
        #elf.ea.uni="222"
        #self.ea.status='ST'
        self.a = Ecouser(uni="222", status='ST')
        print self.a

        self.b = User(first_name="second", last_name="student", username="sstudent", password="sstudent", email="sstudent@email.com")
        #self.eb = self.b.get_profile()
        #self.eb.uni="333"
        #self.eb.status='ST'
        self.b = Ecouser(uni="333", status='ST')
        print self.b

        self.c = User(first_name="third", last_name="student", username="tstudent", password="tstudent", email="tstudent@email.com")
        #self.ec = self.c.get_profile()
        #self.ec.uni="444"
        #self.ec.status='ST'
        self.c = Ecouser(uni="444", status='ST')
        print self.c

        self.d = User(first_name="fourth", last_name="student", username="frstudent", password="frstudent", email="frstudent@email.com")
        #self.ed = self.d.get_profile()
        #self.ed.uni="555"
        #self.ed.status='ST'
        self.d = Ecouser(uni="555", status='ST')

        self.e = User(first_name="first", last_name="instructor", username="finstructor", password="finstructor", email="finstructor@email.com")
        #self.ee = self.e.get_profile()
        #self.ee.uni="111"
        #self.ee.status='IN'
        self.e = Ecouser(uni="111", status='IN')


        self.map1 = Ecomap(title="Test Map 1", ecomap_xml="<data><response>OK</response><isreadonly>false</isreadonly><name>somestudent</name><flashData><circles><circle><radius>499</radius></circle><circle><radius>350</radius></circle><circle><radius>200</radius></circle></circles><supportLevels><supportLevel><text>Very Helpful</text></supportLevel><supportLevel><text>Somewhat Helpful</text></supportLevel><supportLevel><text>Not So Helpful</text></supportLevel></supportLevels><supportTypes><supportType><text>Social</text></supportType><supportType><text>Advice</text></supportType><supportType><text>Empathy</text></supportType><supportType><text>Practical</text></supportType></supportTypes><persons><person><name>green</name><supportLevel>2</supportLevel><supportTypes><support>Advice</support><support>Social</support></supportTypes><x>293</x><y>70</y></person><person><name>yellow</name><supportLevel>1</supportLevel><supportTypes><support>Social</support><support>Empathy</support></supportTypes><x>448</x><y>208</y></person><person><name>red</name><supportLevel>0</supportLevel><supportTypes><support>Social</support><support>Practical</support></supportTypes><x>550</x><y>81.95</y></person></persons></flashData></data>", owner=ea)
        self.map2 = Ecomap(title="Test Map 2", ecomap_xml="<data><response>OK</response><isreadonly>false</isreadonly><name>student</name><flashData><circles><circle><radius>499</radius></circle><circle><radius>350</radius></circle><circle><radius>200</radius></circle></circles><supportLevels><supportLevel><text>Very Helpful</text></supportLevel></flashData></data>", owner=eb)
        self.map3 = Ecomap(title="Test Map 3", ecomap_xml="<data><response>OK</response><isreadonly>false</isreadonly><name>anotherstudent</name><flashData><text>Very Helpful</text></supportLevel><supportLevel><text>Somewhat Helpful</text></supportLevel><supportLevel><text>Not So Helpful</text></supportLevel></supportLevels><supportTypes><supportType><text>Practical</text></supportType></supportTypes><persons><person><name>green</name><supportLevel>2</supportLevel><supportTypes><support>Advice</support><support>Social</support></supportTypes><x>293</x><y>70</y></person><person><name>yellow</name><supportLevel>1</supportLevel><supportTypes><support>Social</support><support>Empathy</support></supportTypes><x>448</x><y>208</y></person><person><name>red</name><supportLevel>0</supportLevel><supportTypes><support>Social</support><support>Practical</support></supportTypes><x>550</x><y>81.95</y></person></persons></flashData></data>", owner=ec)
        self.map4 = Ecomap(title="Test Map 4", ecomap_xml="<supportLevel><text>Somewhat Helpful</text></supportLevel><supportType><text>Social</text></supportType><supportType><text>Advice</text></supportType><supportType><persons><person><name>green</name><supportLevel>2</supportLevel><supportTypes><support>Advice</support><support>Social</support></supportTypes><x>293</x><y>70</y></person><person><name>yellow</name><supportLevel>1</supportLevel><supportTypes><support>Social</support><support>Empathy</support></supportTypes><x>448</x><y>208</y></person><person><name>red</name><supportLevel>0</supportLevel><supportTypes><support>Social</support><support>Practical</support></supportTypes><x>550</x><y>81.95</y></person></persons></flashData></data>", owner=ed)



    def test_uni(self):
        """Make sure the user_name method returns user names as it is supposed to."""
        self.assertEqual(self.a.uni(), "222")
        self.assertEqual(self.b.uni(), "333")
        self.assertEqual(self.c.uni(), "444")
        self.assertEqual(self.d.uni(), "555")
        self.assertEqual(self.e.uni(), "111")


    def test_user_status(self):
        self.assertEqual(self.a.status(), "ST")
        self.assertEqual(self.b.status(), "ST")
        self.assertEqual(self.c.status(), "ST")
        self.assertEqual(self.d.status(), "ST")
        self.assertEqual(self.e.status(), "IN")


    def test_unicode(self):
        self.user.first_name + " " + self.user.last_name
        self.assertEqual(self.ea.user, "first student")
        self.assertEqual(self.eb.user, "second student")
        self.assertEqual(self.ec.user, "third student")
        self.assertEqual(self.ed.user, "fourth student")
        self.assertEqual(self.ee.user, "first instructor")


    def test_title(self):
        self.assertEqual(self.map1.title(), "Test Map 1")
        self.assertEqual(self.map2.title(), "Test Map 2")
        self.assertEqual(self.map3.title(), "Test Map 3")
        self.assertEqual(self.map4.title(), "Test Map 4")


    def test_ecomap_xml(self):
        pass


    def test_owner(self):
        self.assertEqual(self.map1.owner(), ea)
        self.assertEqual(self.map2.owner(), eb)
        self.assertEqual(self.map3.owner(), ec)
        self.assertEqual(self.map4.owner(), ed)



