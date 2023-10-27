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

public class Reseau extends AppCompatActivity {
    private String ip;
    private String port;

    private EditText champIp;
    private EditText champPort;

    private SharedPreferences sharedPreferences;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_reseau);

        champIp = findViewById(R.id.ip);
        champPort = findViewById(R.id.port);

        sharedPreferences = getSharedPreferences(getString(R.string.data), Context.MODE_PRIVATE);
        ip = sharedPreferences.getString(getString(R.string.dataip), "192.168.1.1");
        port = sharedPreferences.getString(getString(R.string.dataport), "10000");

        champIp.setText(ip);
        champPort.setText(port);
    }

    public void save(View v) {
        if (champIp.getText() == null || champIp.getText().toString().equals("") || champPort.getText() == null) {
            Toast.makeText(this, "Les données sont incomplètes", Toast.LENGTH_LONG).show();
            return;
        }

        ip = champIp.getText().toString();
        port = champPort.getText().toString();

        SharedPreferences.Editor editor = sharedPreferences.edit();
        editor.putString(getString(R.string.dataip), ip);
        editor.putString(getString(R.string.dataport), port);
        editor.commit();

        Toast.makeText(this, "Sauvegardé", Toast.LENGTH_SHORT).show();
        finish();
    }
}