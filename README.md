# EDSM Distance Calculator

A Python web application that calculates distances between star systems in Elite Dangerous using the EDSM (Elite Dangerous Star Map) API. The calculator features an intuitive interface for plotting routes, optimizing paths, and managing system coordinates.

![EDSM Calculator Interface](/api/placeholder/800/400)

[![requests](https://img.shields.io/badge/requests-2.31.0-blue)](https://requests.readthedocs.io/)
[![nicegui](https://img.shields.io/badge/nicegui-1.4.5-blue)](https://nicegui.io/)
[![pandas](https://img.shields.io/badge/pandas-2.2.0-blue)](https://pandas.pydata.org/)
[![asyncio](https://img.shields.io/badge/asyncio-3.12.1-blue)](https://docs.python.org/3/library/asyncio.html)
[![json](https://img.shields.io/badge/json-3.12.1-blue)](https://docs.python.org/3/library/json.html)
[![math](https://img.shields.io/badge/math-3.12.1-blue)](https://docs.python.org/3/library/math.html)
[![datetime](https://img.shields.io/badge/datetime-3.12.1-blue)](https://docs.python.org/3/library/datetime.html)
[![itertools](https://img.shields.io/badge/itertools-3.12.1-blue)](https://docs.python.org/3/library/itertools.html)
[![csv](https://img.shields.io/badge/csv-3.12.1-blue)](https://docs.python.org/3/library/csv.html)
[![io](https://img.shields.io/badge/io-3.12.1-blue)](https://docs.python.org/3/library/io.html)
[![os](https://img.shields.io/badge/os-3.12.1-blue)](https://docs.python.org/3/library/os.html)

## Features

- **System Distance Calculation**: Calculate precise distances between multiple star systems
- **Route Optimization**: Automatically finds the shortest path through all selected systems
- **Jump Range Planning**: Estimates required jumps based on your ship's jump range
- **Route History**: Keeps track of previously calculated routes
- **Import/Export**: Support for CSV import and export of system coordinates
- **Autocomplete**: System name suggestions while typing
- **Real-time Updates**: Instant distance calculations and route optimizations
- **Dark Mode Interface**: Easy on the eyes for those long exploration sessions

## Installation

1. Clone the repository:

```bash
git clone https://github.com/BattlemasterLoL/ed-multi-pather.git
cd ed-multi-pather
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Dependencies

- requests
- nicegui
- pandas
- asyncio
- python-csv

## Usage

1. Start the application:

```bash
python main.py
```

2. Open your web browser and navigate to `http://localhost:8080`

3. To calculate a route:

   - Enter your ship's jump range (optional)
   - Add systems using the system name input
   - Click "Calculate Route" to see both direct and optimized paths
   - View estimated jumps if jump range was provided

4. Additional features:
   - Export your route to CSV by clicking "Export Route"
   - Import routes from CSV using the "Import Route" button
   - View route history in the bottom panel
   - Clear all systems and start over using "Clear All"

## CSV Format

When importing or exporting routes, the CSV file should have the following format:

```csv
System Name,X,Y,Z
Sol,0,0,0
Sagittarius A*,25.21968,-20.90947,25899.96094
```

## API Integration

The application uses the EDSM API to fetch star system coordinates. The API endpoint used is:

```
https://www.edsm.net/api-v1/system
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [EDSM](https://www.edsm.net/) for providing the star system coordinate data
- [NiceGUI](https://nicegui.io/) for the web interface framework
- The Elite Dangerous community for inspiration and support

## Support

If you encounter any issues or have suggestions for improvements, please open an issue on the GitHub repository.
