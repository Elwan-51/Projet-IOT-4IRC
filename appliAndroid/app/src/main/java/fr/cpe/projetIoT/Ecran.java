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

/**
 * Class corresponding to the screen configuration activity
 */
public class Ecran extends AppCompatActivity {
    private List<ItemModel> itemList = new ArrayList<>();
    private ItemAdapter itemAdapter;
    private RecyclerView recyclerView;
    private SharedPreferences sharedPreferences;

    private String TAG = "Adrien/Ecran";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // Keep the call to onCreate's parent class
        super.onCreate(savedInstanceState);

        // We define the activity layout
        setContentView(R.layout.activity_ecran);

        // We retrieve the data present in the sharedPreferences
        sharedPreferences = getSharedPreferences(getString(R.string.data), Context.MODE_PRIVATE);

        recyclerView = findViewById(R.id.ordonner);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        // Create elements to be freely arranged in a chosen order
        itemList.add(new ItemModel("Température"));
        itemList.add(new ItemModel("Luminosité"));

        itemAdapter = new ItemAdapter(itemList);
        recyclerView.setAdapter(itemAdapter);
        ItemTouchHelper itemTouchHelper = new ItemTouchHelper(new ItemTouchHelperCallback());
        itemTouchHelper.attachToRecyclerView(recyclerView);
    }

    /**
     * When the "save" button is clicked (defined in res/layout/activity_ecran.xml)
     * @param View view
     */
    public void save(View view){
        // Retrieve network values
        String ip = sharedPreferences.getString(getString(R.string.dataip), "192.168.1.1");
        String port = sharedPreferences.getString(getString(R.string.dataport), "10000");

        // The MyThread class is used to send data to the server
        MyThreadEventListener listener = new MyThreadEventListener() {
            @Override
            public void onEventInMyThread(byte[] data) {
                new Handler(Looper.getMainLooper()).post(new Runnable() {
                    @Override
                    public void run() {
                        // Do Something in the Main Thread (Graphic Thread)
                        try {
                            JSONObject obj = new JSONObject(new String(data));
                            //Log.d(TAG, "run2: "+obj.getString("message"));
                            // If success is received, the user is informed that the request has been saved
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

        // Run the Thread with the temperature and brightness objects ordered
        MyThread thread = new MyThread(listener, ip, port, getOrderedItems());
        thread.start();
    }

    private class ItemTouchHelperCallback extends ItemTouchHelper.Callback {
        @Override
        public int getMovementFlags(RecyclerView recyclerView, RecyclerView.ViewHolder viewHolder) {
            int dragFlags = ItemTouchHelper.UP | ItemTouchHelper.DOWN;
            return makeMovementFlags(dragFlags, 0);
        }

        /**
         * When items are moved, their positions in the List are exchanged.
         *
         * @param RecyclerView recyclerView: The RecyclerView associated with the ItemTouchHelper.
         * @param RecyclerView.ViewHolder viewHolder: The ViewHolder of the item being moved.
         * @param RecyclerView.ViewHolder target: The ViewHolder of the target position where the item is dropped.
         * @return boolean true: Returns true if the move operation is successful.
         */
        @Override
        public boolean onMove(RecyclerView recyclerView, RecyclerView.ViewHolder viewHolder, RecyclerView.ViewHolder target) {
            // Echanger les positions des éléments dans la liste
            int fromPosition = viewHolder.getAdapterPosition();
            int toPosition = target.getAdapterPosition();
            Collections.swap(itemList, fromPosition, toPosition);
            itemAdapter.notifyItemMoved(fromPosition, toPosition);
            return true;
        }

        /**
         * This method is called when an item is swiped, but no action is taken in our case.
         *
         * @param RecyclerView.ViewHolder viewHolder: The ViewHolder of the swiped item.
         * @param int direction: The direction in which the item is swiped.
         */
        @Override
        public void onSwiped(@NonNull RecyclerView.ViewHolder viewHolder, int direction) {}
    }

    /**
     * Allows retrieving sorted items
     * Function returning a String containing the first letter of the ordered temperature and luminosity items according to user choices
     * @return String order
     */
    private String getOrderedItems() {
        String order = "";
        for (ItemModel item : itemList) {
            Log.d(TAG, "order: "+item);
            order += item.getItemName().charAt(0);
        }
        return order;
    }
}