package fr.cpe.projetIoT;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

/**
 * Class for sending and receiving data over UDP to the server.
 * This class is created based on the IoT course.
 */
public class MyThread extends Thread {
    private MyThreadEventListener listener;
    private String ip;
    private String port;
    private String message;

    public MyThread(
            MyThreadEventListener listener,
            String ip,
            String port,
            String message
    ) {
        this.listener = listener;
        this.ip = ip;
        this.port = port;
        this.message = message;
    }

    public void run() {
        DatagramSocket UDPSocket = null;
        InetAddress address;
        byte[] retour = new byte[1024];

        try {
            UDPSocket = new DatagramSocket();
            address = InetAddress.getByName(ip);
            byte[] data = message.getBytes();
            DatagramPacket packet = new DatagramPacket(data, data.length, address, Integer.parseInt(port));
            UDPSocket.send(packet);
        
            retour = new byte[1024];
            DatagramPacket packet = new DatagramPacket(retour,retour.length);
            UDPSocket.receive(packet); //bloquant
            int size = packet.getLength();
        } catch (IOException e) {
            e.printStackTrace();
        }
        listener.onEventInMyThread(retour);
    }
}
