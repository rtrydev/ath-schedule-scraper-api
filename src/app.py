from shared.services.schedule_scraper_service import ScheduleScraperService

svc = ScheduleScraperService()

print(svc.fetch_branch_data(branch_id='8209', branch_type='1', branch_link='1'))
