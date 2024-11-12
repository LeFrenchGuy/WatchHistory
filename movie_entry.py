class MovieEntry:
    def __init__(self, title, date, is_cinema):
        self.title = title
        self.date = date
        self.is_cinema = is_cinema

    def __repr__(self):
        return f"MovieEntry(title={self.title}, date={self.date}, is_cinema={self.is_cinema})"