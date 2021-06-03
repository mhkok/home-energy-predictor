import get_data_p1
import unittest
from freezegun import freeze_time

@freeze_time("2021-06-03 16:24:00")

class TestGetDataP1Class(unittest.TestCase):
    """
    Test the Get Data P1 functionality
    """     
    def setUp(self):
        self.usage_dict = {'current_power_usage_kwh': 0.13, 'gas_usage_m3': 632.681, 'datetime': '03-06-2021-16-24', 'peak_hours_kwh': 3096.193, 'peak_hours_returned_kwh': 223.795, 'off_peak_hours_kwh': 2493.568, 'off_peak_hours_returned_kwh': 102.211, 'current_power_returned_kwh': 0.0}
        self.stack = ['/ISK5\\2M550E-1012', '', '1-3:0.2.8(50)', '0-0:1.0.0(210603171150S)', '0-0:96.1.1(4530303433303036383837313336373137)', '1-0:1.8.1(002493.568*kWh)', '1-0:1.8.2(003096.193*kWh)', '1-0:2.8.1(000102.211*kWh)', '1-0:2.8.2(000223.795*kWh)', '0-0:96.14.0(0002)', '1-0:1.7.0(00.130*kW)', '1-0:2.7.0(00.000*kW)', '0-0:96.7.21(00017)', '0-0:96.7.9(00025)', '1-0:99.97.0(10)(0-0:96.7.19)(190603065743S)(0000150603*s)(190604065307S)(0000050149*s)(190604143503S)(0000002017*s)(190605065649S)(0000050775*s)(190606065629S)(0000049513*s)(190607065825S)(0000050886*s)(190608075459S)(0000055402*s)(190610075037S)(0000150284*s)(190610114351S)(0000004477*s)(201008190511S)(0000017122*s)', '1-0:32.32.0(00012)', '1-0:32.36.0(00001)', '0-0:96.13.0()', '1-0:32.7.0(232.0*V)', '1-0:31.7.0(001*A)', '1-0:21.7.0(00.123*kW)', '1-0:22.7.0(00.000*kW)', '0-1:24.1.0(003)', '0-1:96.1.0(4730303339303031393134313430323139)', '0-1:24.2.1(210603171000S)(00632.681*m3)', '!5836']

    def test_process_p1_output(self):
        """
        Test that checks if the P1 output is correct after being processed
        """
        result = get_data_p1.process_p1_output(self.stack)
        self.assertEqual(result, self.usage_dict)

    def test_create_json(self):
        """
        Test that the output is of type JSON and has the right contents
        """
        result = get_data_p1.create_json(self.usage_dict)
        self.assertEqual(result, "p1_raw_data_03-06-2021-16-24.json")

if __name__ == '__main__':
    unittest.main()