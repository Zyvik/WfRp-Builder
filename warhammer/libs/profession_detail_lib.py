from warhammer.models import StatsModel


def create_modals(skill_list, skills_string):
    for skill in skill_list:
        modal_link = f"<a href=\"#\" data-toggle=\"modal\" data-target=\"#{skill.slug}\" data-en=\"{skill.name_en}\">{skill.name}</a>"
        skills_string = skills_string.replace(skill.name, modal_link)
    return skills_string


def prepare_stats_for_display(profession):
    stats_list = profession.stats.split('\n')
    all_stats = StatsModel.objects.all()
    prof_stats = []
    prof_stats_bonus = []
    for i, stat in enumerate(all_stats):
        if stats_list[i].replace('\r', '') != '-':
            prof_stats.append(stat)
            prof_stats_bonus.append(stats_list[i])
    stats_list = zip(prof_stats, prof_stats_bonus)
    return stats_list
