from django.test import SimpleTestCase
from django.urls import resolve, reverse
from warhammer import views


class TestUrls(SimpleTestCase):
    # tuple containing urls and instances of class based views
    class_based_tuple = (
        (reverse('wh:index'), views.IndexView),
        (reverse('wh:professions'), views.ProfessionList),
        (reverse('wh:character_screen', args=[1]), views.CharacterScreen),
        (reverse('wh:register'), views.RegisterView),
        (reverse('wh:login'), views.LoginView),
        (reverse('wh:contact'), views.ContactView),
        (reverse('wh:abilities_list'), views.AbilityList),
        (reverse('wh:skills_list'), views.SkillList)
    )

    # tuple containing urls and instances of function based views
    func_based_tuple = (
        (reverse('wh:race'), views.choose_race),
        (reverse('wh:stats', args=['slug']), views.roll_stats),
        (reverse('wh:selected_profession', args=['slug']), views.profession_detail),
        (reverse('wh:logout'), views.logout_view)
    )

    def test_urls_to_CBVs(self):
        for url, view in self.class_based_tuple:
            called_view = resolve(url).func.view_class
            self.assertEquals(called_view, view, msg=url)

    def test_urls_to_FBVs(self):
        for url, view in self.func_based_tuple:
            self.assertEquals(resolve(url).func, view, msg=url)
