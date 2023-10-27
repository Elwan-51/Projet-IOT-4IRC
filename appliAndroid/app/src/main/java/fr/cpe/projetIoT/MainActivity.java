package fr.cpe.projetIoT;

import androidx.appcompat.app.AppCompatActivity;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class MainActivity extends AppCompatActivity {
    private SharedPreferences sharedPreferences;
    private String ip;
    private String port;
    private SwipeRefreshLayout pullToRefresh;
    private String TAG = "Adrien/MainActivity";


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        sharedPreferences = getSharedPreferences(getString(R.string.data), Context.MODE_PRIVATE);

        pullToRefresh = findViewById(R.id.pullToRefresh);
        pullToRefresh.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                getData();
            }
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        getData();
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        super.onCreateOptionsMenu(menu);
        MenuInflater inflater = getMenuInflater();
        inflater.inflate(R.menu.menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle item selection.
        if (item.getItemId() == R.id.ecran) {
            config_ecran();
            return true;
        } else if (item.getItemId() == R.id.reseau) {
            config_reseau();
            return true;
        } else {
            return super.onOptionsItemSelected(item);
        }
    }

    private void config_ecran() {
        Intent intent = new Intent(this, Ecran.class);
        startActivity(intent);
    }

    private void config_reseau() {
        Intent intent = new Intent(this, Reseau.class);
        startActivity(intent);
    }

    private void getData() {
        ip = sharedPreferences.getString(getString(R.string.dataip), "192.168.1.1");
        port = sharedPreferences.getString(getString(R.string.dataport), "10000");
        MyThreadEventListener listener = new MyThreadEventListener() {
            @Override
            public void onEventInMyThread(byte[] data) {
                new Handler(Looper.getMainLooper()).post(new Runnable() {
                    @Override
                    public void run() {
                        //Do Something in the Main Thread (Graphic Thread)
                        Log.d(TAG, "run: "+new String(data));
                        try {
                            JSONArray arr = new JSONArray(new String(data));
                            for(int i = 0; i < 2; i++) {
                                JSONObject obj = (JSONObject) arr.get(i);
                                double value = obj.getDouble("value");
                                if (obj.getString("type").equals("lumi")) {
                                    ((TextView)findViewById(R.id.luminosite)).setText(value+" Lux");
                                } else if (obj.getString("type").equals("temp")) {
                                    ((TextView)findViewById(R.id.temperature)).setText(value+" °C");
                                    int red;
                                    int blue;
                                    if (value > 30) {
                                        red = 255;
                                        blue = 0;
                                    } else if (value <= 16) {
                                        red = 0;
                                        blue = 255;
                                    } else {
                                        red = (int) ((255/14)*(value - 16));
                                        blue = 255 - red;
                                    }
                                    int color = Color.argb(255, red, 0, blue);
                                    ((ImageView)findViewById(R.id.imageTher)).setColorFilter(color);
                                }
                            }
                            findViewById(R.id.loadingMessage).setVisibility(View.INVISIBLE);
                            findViewById(R.id.table).setVisibility(View.VISIBLE);
                            if (pullToRefresh.isRefreshing()) { pullToRefresh.setRefreshing(false); }
                        } catch (JSONException e) {
                            throw new RuntimeException(e);
                        }
                    }
                });
            }
        };
        MyThread thread = new MyThread(listener, ip, port, "getValues()");
        thread.start();
    }
}
