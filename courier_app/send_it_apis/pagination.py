class Kurasa(object):
    """Implements pagination of lists."""

    def __init__(self, mylist = [], post_per_page = 1, *args):
        """
        Initialize a Kurasa object with the list you want to slice.

        Usage:
        test_list = [1,3,4,5,6,7,8,9,5,6,67,2,3,5,6,7,8,7,5,3,2,3,5,6,7,8,8]       
        kur = Kurasa(sample_list, 5)
        kur.no_of_pages # 6
        kur.has_next(3) #True
        kur.get_items(3) #[67, 2, 3, 5, 6]
        
        Methods

        """
        self.page_posts = post_per_page
        self.list_data = mylist
        self.no_of_pages = 0

        pages = len(self.list_data)/self.page_posts
        self.no_of_pages = int(pages) + 1

    
    def has_next(self, current_number):
        if self.no_of_pages == 0:
            return False
        elif current_number < self.no_of_pages:
           return True
        else:
            return False    

    def has_prev(self, current_number):
        if self.no_of_pages == 0:
            return False
        elif current_number > 1:
           return True
        else:
            return False

    def next_page(self, current_number):
        return current_number + 1

    def prev_page(self, current_number):
        return current_number - 1

    def get_items(self, current_number):
        end_index = (current_number * self.page_posts)
        start_index = end_index - self.page_posts

        if end_index > len(self.list_data):
            end_index = len(self.list_data)

        return self.list_data[start_index:end_index]
