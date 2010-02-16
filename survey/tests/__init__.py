# TODO: Find out how to run configure the test framework to run the test on :
# sqlite, mysql, postgresql if the db are installed
from survey.tests import test_models, test_urls, test_images

#Define the doctest
__test__ = {
    "models" : test_models.test_cases,
    "urls" : test_urls.test_cases,
    "images" : test_images.test_cases,
}
