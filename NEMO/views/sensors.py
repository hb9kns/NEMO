from pymodbus.client.sync import ModbusTcpClient
from smtplib import SMTPException
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from NEMO.decorators import disable_session_expiry_refresh
from NEMO.models import Sensor
from NEMO.views.customization import get_customization

@staff_member_required
@disable_session_expiry_refresh
def read_sensors(request):
    sensors = Sensor.objects.all()
    sensor_data = []
    dictionary = {}
    for sensor in sensors:
        client = ModbusTcpClient(sensor.address.server, port=502, timeout=1)
        try:
            client.connect()
            if sensor.sensor_type == Sensor.SensorType.DIGITAL:
                reply = client.read_discrete_inputs(sensor.channel,1,unit=1)
                sensor_reading = reply.bits[0]
                sensor_response = {'sensor_name': sensor.name, 'sensor_reading':sensor_reading}
                if sensor.digital_sensor_alert and sensor.email and str(sensor_reading) != sensor.last_value:
                    if sensor.digital_alert_value and sensor_reading:
                        send_sensor_alert_email(sensor, str(sensor_reading))
                        #send_sensor_alert_email()
                    elif not sensor.digital_alert_value and not sensor_reading:
                        send_sensor_alert_email(sensor, str(sensor_reading))
                        #send_sensor_alert_email()
            else:
                reply = client.read_input_registers(sensor.channel,1,unit=1)
                sensor_reading = round(reply.registers[0]*sensor.conversion_factor,2)
                if sensor.high_alert_value and sensor.email:
                    if sensor_reading > sensor.high_alert_value and float(sensor.last_value) <= sensor.high_alert_value:
                        send_sensor_alert_email(sensor, str(sensor_reading))
                        #send_sensor_alert_email()
                if sensor.low_alert_value and sensor.email:
                    if sensor_reading < sensor.low_alert_value and float(sensor.last_value) >= sensor.low_alert_value:
                        send_sensor_alert_email(sensor, str(sensor_reading))
                        #send_sensor_alert_email()
            sensor.last_value = str(sensor_reading)
            sensor.save()
            client.close()
        except:
            sensor_reading = "Could Not Connect"
        sensor_response = {'sensor_name': sensor.name, 'sensor_reading':sensor_reading}
        sensor_data.append(sensor_response)
        client.close()
    dictionary['sensor_data'] = sensor_data
    return render(request, 'sensors/sensor_data.html', dictionary)

@staff_member_required
def sensors(request):
    return render(request, 'sensors/sensors.html')

def send_sensor_alert_email(sensor, value):
    try:
        user_office_email = get_customization('user_office_email_address')
        recipient = sensor.email
        recipient_list = [recipient]
        sender = user_office_email
        subject = f'Sensor Alert for {sensor.name}'
        body = f'The following sensor has recorded a value past its alert threshold: {sensor.name} with value {value}'
        email = EmailMultiAlternatives(subject, from_email=sender, to=recipient_list)
        email.attach_alternative(body, 'text/html')
        email.send()
    except:
        pass
#
# client = ModbusTcpClient(#server#)
# client.connect()
# client.write_coil(#channel, command, unit=1)
# client.read_coils(#channel, number of coils to read, unit=1)
#client.read_input_registers()
#
# response = client.read_holding_registers(
#     address=register,  # 40161
#     count=count,       # 2
#     unit=device)       # 4
#
# decoder = BinaryPayloadDecoder.fromRegisters(
#     registers=response.registers,
#     byteorder=Endian.Big,
#     wordorder=Endian.Big)
#
# value = decoder.decode_32bit_float()
#
# client.close()
