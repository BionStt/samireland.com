import os
from .base import FunctionalTest
from samireland.settings import BASE_DIR, MEDIA_ROOT

class MediaTest(FunctionalTest):

    def setUp(self):
        FunctionalTest.setUp(self)
        self.files_at_start = os.listdir(MEDIA_ROOT)


    def tearDown(self):
        for f in os.listdir(MEDIA_ROOT):
            if f not in self.files_at_start:
                try:
                    os.remove(MEDIA_ROOT + "/" + f)
                except OSError:
                    pass
        FunctionalTest.tearDown(self)



class MediaUploadPageTests(MediaTest):

    def test_can_upload_images(self):
        self.login()
        self.get("/")

        # There is a media link in the header
        header = self.browser.find_element_by_tag_name("header")
        media_link = header.find_element_by_id("media-link")

        # They click it and are taken to the media page
        media_link.click()
        self.check_page("/media/")

        # There is a header, and a div for the media grid
        self.check_title("Media")
        self.check_h1("Media")
        grid = self.browser.find_element_by_id("media-grid")

        # The grid is empty
        self.assertEqual(len(grid.find_elements_by_class_name("media-square")), 0)

        # There is a form for uploading media
        form = self.browser.find_element_by_tag_name("form")

        # There is a file input and a name input
        file_input, name_input = form.find_elements_by_tag_name("input")[:2]
        self.assertEqual(file_input.get_attribute("type"), "file")
        self.assertEqual(name_input.get_attribute("type"), "text")

        # They upload an image and call it 'test image'
        file_input.send_keys(BASE_DIR + "/samireland/static/images/favicon-96x96.png")
        name_input.send_keys("test-image")

        # They click the submit button
        submit_button = form.find_elements_by_tag_name("input")[-1]
        submit_button.click()

        # They are still on the same page
        self.check_page("/media/")

        # The grid now has one item
        grid = self.browser.find_element_by_id("media-grid")
        media = grid.find_elements_by_class_name("media-square")
        self.assertEqual(len(media), 1)

        # The media's text is the title
        self.assertIn("test-image", media[0].text)

        # It has the image as background
        self.assertTrue(media[0].value_of_css_property("background-image").endswith(".png\")"))


    def test_cannot_upload_media_with_duplicate_title(self):
        self.login()
        self.get("/media/")

        # There is a form for uploading media
        form = self.browser.find_element_by_tag_name("form")
        file_input, name_input = form.find_elements_by_tag_name("input")[:2]
        self.assertEqual(file_input.get_attribute("type"), "file")
        self.assertEqual(name_input.get_attribute("type"), "text")

        # They upload an image correctly
        file_input.send_keys(BASE_DIR + "/samireland/static/images/favicon-96x96.png")
        name_input.send_keys("test-image")
        submit_button = form.find_elements_by_tag_name("input")[-1]
        self.click(submit_button)

        # They are still on the same page
        self.check_page("/media/")

        # They upload an image with duplicate name
        form = self.browser.find_element_by_tag_name("form")
        file_input, name_input = form.find_elements_by_tag_name("input")[:2]
        self.assertEqual(file_input.get_attribute("type"), "file")
        self.assertEqual(name_input.get_attribute("type"), "text")
        file_input.send_keys(BASE_DIR + "/samireland/static/images/favicon-96x96.png")
        name_input.send_keys("test-image")
        submit_button = form.find_elements_by_tag_name("input")[-1]
        self.click(submit_button)

        # The grid still only has one element
        grid = self.browser.find_element_by_id("media-grid")
        self.assertEqual(len(grid.find_elements_by_class_name("media-square")), 1)

        # The form has an error message
        form = self.browser.find_element_by_tag_name("form")
        error = form.find_element_by_class_name("error-message")
        self.assertEqual(error.text, "There is already a file with title.")
