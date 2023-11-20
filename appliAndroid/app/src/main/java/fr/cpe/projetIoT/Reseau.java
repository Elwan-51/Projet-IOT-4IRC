package fr.cpe.projetIoT;

import static com.google.android.material.internal.ContextUtils.getActivity;

import static java.lang.Integer.parseInt;

import androidx.appcompat.app.AppCompatActivity;

import android.annotation.SuppressLint;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

/**
 * Class corresponding to the network configuration activity
 */
public class Reseau extends AppCompatActivity {
    private String ip;
    private String port;

    private EditText champIp;
    private EditText champPort;

    private SharedPreferences sharedPreferences;

    /**
     * Called when the network configuration activity is created.
     * @param Bundle savedInstanceState
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // Retain the call to the parent class's onCreate method
        super.onCreate(savedInstanceState);

        // Set the layout for the activity
        setContentView(R.layout.activity_reseau);

        // Define the IP and Port fields
        champIp = findViewById(R.id.ip);
        champPort = findViewById(R.id.port);

        // Retrieve data from SharedPreferences
        sharedPreferences = getSharedPreferences(getString(R.string.data), Context.MODE_PRIVATE);
        ip = sharedPreferences.getString(getString(R.string.dataip), "192.168.1.1");
        port = sharedPreferences.getString(getString(R.string.dataport), "10000");

        // Fill in the fields based on the data already present in SharedPreferences
        champIp.setText(ip);
        champPort.setText(port);
    }

    /**
     * Called when the "save" button is clicked (defined in res/layout/activity_reseau.xml).
     * @param View v
     */
    public void save(View v) {
        // Before saving the data, check if the fields are filled
        if (champIp.getText() == null || champIp.getText().toString().equals("") || champPort.getText() == null) {
            Toast.makeText(this, "Les données sont incomplètes", Toast.LENGTH_LONG).show();
            return;
        }

        // Retrieve the values (IP, port)
        ip = champIp.getText().toString();
        port = champPort.getText().toString();

       // Write the new values to SharedPreferences
        SharedPreferences.Editor editor = sharedPreferences.edit();
        editor.putString(getString(R.string.dataip), ip);
        editor.putString(getString(R.string.dataport), port);
        editor.commit();

        // Inform the user that it has been saved successfully and exit the configuration activity
        Toast.makeText(this, "Sauvegardé", Toast.LENGTH_SHORT).show();
        finish();
    }
}