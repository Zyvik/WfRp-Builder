from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from warhammer.models import CharacterModel


class TestCreateCharacter(TestCase):
    """
    Tests Views with user not logged in
    """
    fixtures = ['fixtures.json']
    client = Client()

    # query parameters for roll_stats
    roll_stats_query = {
        'ww': 20,
        'us': 20,
        'k': 20,
        'odp': 20,
        'int': 20,
        'sw': 20,
        'ogd': 20,
        'zr': 20,
        'zyw': 10,
        'pp': 10,
        'prof': 100
    }

    def test_choose_race_GET_no_query(self):
        # test valid slugs
        slugs = ['czlowiek', 'elf', 'krasnolud', 'niziolek']
        for slug in slugs:
            url = reverse('wh:stats', args=[slug])
            response = self.client.get(url)
            self.assertEquals(response.status_code, 200)
        # test invalid slug
        url = reverse('wh:stats', args=['foobar'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_roll_stats_GET_query(self):
        # valid queryset - pass to customize_character
        url = reverse('wh:stats', args=['czlowiek'])
        response = self.client.get(url, data=self.roll_stats_query)
        template_name = response.templates[0].name
        self.assertEquals(template_name, 'warhammer/customize_character.html')
        # invalid queryset - stay on roll-stats
        invalid_query = self.roll_stats_query.copy()
        invalid_query['prof'] = 0
        url = reverse('wh:stats', args=['czlowiek'])
        response = self.client.get(url, data=invalid_query)
        template_name = response.templates[0].name
        self.assertEquals(template_name, 'warhammer/roll_stats.html')

    def test_roll_stats_POST(self):
        # manualy create valid query for GET request
        get_query_str = "?"
        for name, value in self.roll_stats_query.items():
            get_query_str += f"{name}={value}&"
        get_query_str = get_query_str[:-1]  # remove last '&'
        url = reverse('wh:stats', args=['czlowiek'])
        url += get_query_str
        # valid POST
        post_data = {
            'name': 'foobar',
            '0_prof_skills': 'PLOTKOWANIE',
            '1_prof_skills': 'HAZARD',
            '0_prof_abilities': 'ROZBRAJANIE',
            'develop_stat': 'WW',
            'coins': '20',
            '0_random_ability': '1',  # Bardzo silny
            '1_random_ability': '100'  # Widzienie w ciemności
        }
        response = Client().post(url, data=post_data)
        # check if redirected (to character screen)
        self.assertEquals(response.status_code, 302)
        # check if character was created
        character_count = CharacterModel.objects.count()
        self.assertEquals(character_count, 3)


class TestIndexView(TestCase):

    def test_IndexView(self):
        url = reverse('wh:index')
        response = Client().get(url)
        characters = response.context.get('your_characters')
        form = response.context.get('form')
        self.assertFalse(characters)
        self.assertFalse(form)

    def test_IndexView_POST(self):
        url = reverse('wh:index')
        response = Client().post(url)
        self.assertEquals(response.status_code, 302)


class TestRegisterView(TestCase):
    fixtures = ['fixtures.json']
    url = reverse('wh:register')

    def test_RegisterView_GET_anonymous(self):
        response = Client().get(self.url)
        self.assertTrue(response.context.get('form', False))

    def test_RegisterView_POST_anonymous(self):
        # Valid POST data
        request_data = {
            'login': 'foobar',
            'password': 'foobar',
            'confirm_password': 'foobar'
        }
        response = Client().post(self.url, data=request_data)
        last_user = User.objects.last()
        self.assertEquals(last_user.username, 'foobar')  # check last user
        self.assertEquals(response.status_code, 302)  # check if redirected

        # invalid POST - user already exists (iexact name)
        request_data = {
            'login': 'FOOBAR',
            'password': 'foobar',
            'confirm_password': 'foobar'
        }
        response = Client().post(self.url, data=request_data)
        last_user = User.objects.last()
        template_name = response.templates[0].name
        self.assertEquals(response.status_code, 200)
        self.assertEquals('warhammer/register.html', template_name)
        self.assertNotEquals(last_user.username, 'FOOBAR')
