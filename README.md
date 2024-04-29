# Flashcard App with Streamlit

This is a simple flashcard application built with Streamlit, a popular Python library for creating interactive web applications. The app allows users to review flashcards, add new flashcards, search for specific flashcards, and view all flashcards.

## Features

- **Review Flashcards:** Review flashcards one by one and categorize their difficulty level as easy, medium, or hard.
- **Add Flashcards:** Add new flashcards with questions, answers, and optional tags.
- **Search Flashcards:** Search for specific flashcards by entering keywords.
- **View All Flashcards:** View all flashcards or filter them by tags.

## Getting Started

Follow the instructions below to set up and run the flashcard app locally:

1. **Clone the Repository:**

   ```bash
   https://github.com/raman-r-4978/flashcard.git
   ```

2. **Install Dependencies:**

   ```bash
   cd flashcard-app
   pip install -r requirements.txt
   ```

3. **Run the App:**

   ```bash
   streamlit run app.py --server.port 8501
   ```

   The app will start running locally and open in your default web browser.


## Code Formatting

This project follows code formatting standards using `isort` for import sorting and `black` for code formatting.

To format the code, run the following commands:

```bash
isort app.py utils.py
black app.py utils.py
```

## CSS Styles

The CSS styles used in the app are inspired by [this repository](https://github.com/TomJohnH/streamlit-po/tree/main). They are used to enhance the visual appearance of the app.

## Contributing

Contributions are welcome! If you have any suggestions, feature requests, or bug reports, please open an issue or submit a pull request.

Feel free to customize and expand upon to better suit your project's needs.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

---