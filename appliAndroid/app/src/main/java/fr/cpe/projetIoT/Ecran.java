package fr.cpe.projetIoT;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.ItemTouchHelper;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Ecran extends AppCompatActivity {
    private List<ItemModel> itemList = new ArrayList<>();
    private ItemAdapter itemAdapter;
    private RecyclerView recyclerView;
    private SharedPreferences sharedPreferences;

    private String TAG = "Adrien/Ecran";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_ecran);

        sharedPreferences = getSharedPreferences(getString(R.string.data), Context.MODE_PRIVATE);

        recyclerView = findViewById(R.id.ordonner);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        // Créer les éléments à ordonner librement selon l'ordre actuel
        itemList.add(new ItemModel("Température"));
        itemList.add(new ItemModel("Luminosité"));

        itemAdapter = new ItemAdapter(itemList);
        recyclerView.setAdapter(itemAdapter);

        ItemTouchHelper itemTouchHelper = new ItemTouchHelper(new ItemTouchHelperCallback());
        itemTouchHelper.attachToRecyclerView(recyclerView);
    }

    public void save(View view){
        String ip = sharedPreferences.getString(getString(R.string.dataip), "192.168.1.1");
        String port = sharedPreferences.getString(getString(R.string.dataport), "10000");
        MyThreadEventListener listener = new MyThreadEventListener() {
            @Override
            public void onEventInMyThread(byte[] data) {
                new Handler(Looper.getMainLooper()).post(new Runnable() {
                    @Override
                    public void run() {
                        //Do Something in the Main Thread (Graphic Thread)
                        try {
                            JSONObject obj = new JSONObject(new String(data));
                            //Log.d(TAG, "run2: "+obj.getString("message"));
                            if (obj.getString("message").equals("Success")) {
                                Toast.makeText(Ecran.this, "Sauvegardé", Toast.LENGTH_SHORT).show();
                                //finish();
                            }
                        } catch (JSONException e) {
                            throw new RuntimeException(e);
                        }
                    }
                });
            }
        };
        MyThread thread = new MyThread(listener, ip, port, getOrderedItems());
        thread.start();
    }

    private class ItemTouchHelperCallback extends ItemTouchHelper.Callback {
        @Override
        public int getMovementFlags(RecyclerView recyclerView, RecyclerView.ViewHolder viewHolder) {
            int dragFlags = ItemTouchHelper.UP | ItemTouchHelper.DOWN;
            return makeMovementFlags(dragFlags, 0);
        }

        @Override
        public boolean onMove(RecyclerView recyclerView, RecyclerView.ViewHolder viewHolder, RecyclerView.ViewHolder target) {
            // Echanger les positions des éléments dans la liste
            int fromPosition = viewHolder.getAdapterPosition();
            int toPosition = target.getAdapterPosition();
            Collections.swap(itemList, fromPosition, toPosition);
            itemAdapter.notifyItemMoved(fromPosition, toPosition);
            return true;
        }

        @Override
        public void onSwiped(@NonNull RecyclerView.ViewHolder viewHolder, int direction) {}
    }

    private String getOrderedItems() {
        String order = "";
        for (ItemModel item : itemList) {
            Log.d(TAG, "order: "+item);
            order += item.getItemName().charAt(0);
        }
        return order;
    }
}