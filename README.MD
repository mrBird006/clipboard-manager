# Clipboard Manager

This prototype clipboard manager allows you to listen for copy and cut hotkey events and sort the text in your clipboard. It enables you to create a queue of elements and paste them in your intended order. Additionally, it provides an option to create a smooth typing animation, which is useful for preparing programming tutorials without live human coding errors.

## Getting Started

### Prerequisites

Ensure you have the following installed on your machine:
- Python 3.x
- pip (Python package installer)

### Creating a Virtual Environment (Optional but Recommended)

It's recommended to create a virtual environment to manage your project's dependencies, ensuring they are isolated from other projects.

To create a virtual environment, run the following commands:

```bash
# Create a virtual environment
python -m venv myenv

# Activate the virtual environment
# On Windows
myenv\Scripts\activate
# On macOS and Linux
source myenv/bin/activate
```

### Installation

After activating your virtual environment, install the required packages:

```bash
pip install -r requirements.txt
```

### Usage Guidance

1. Run the script:

```bash
python index.py
```

2. Select text and press `Ctrl+C` or `Ctrl+X` to add it to the clipboard manager.

3. Sort the text in the order you want to paste it.

4. Press `Ctrl+Alt+1` to paste the text with a typing animation.

## Features

- **Clipboard Management**: Listen for copy and cut hotkey events.
- **Queue System**: Organize and sort copied text in the order you intend to paste.
- **Smooth Typing Animation**: Paste text with a smooth typing animation, ideal for creating error-free programming tutorials.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
